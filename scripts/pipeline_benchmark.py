"""
Headless end-to-end benchmark of the DeepFaceLive pipeline:
  YoloV5Face detection -> Google FaceMesh landmarks -> alignment -> DFM face swap -> merge (CPU)

Uses the same modelhub classes and default parameters as the GUI backends.

Usage:
  python scripts/pipeline_benchmark.py --dfm userdata/dfm_models/Joker.dfm --input video.mp4 [--frames 300] [--out-dir out] [--cpu]
"""
import argparse
import sys
import time
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

import cv2
import numexpr as ne
import numpy as np

from modelhub import onnx as onnx_models
from modelhub.DFLive.DFMModel import DFMModel
from xlib import avecl as lib_cl
from xlib import onnxruntime as lib_ort
from xlib.face import ELandmarks2D, FLandmarks2D, FRect
from xlib.image import ImageProcessor


def merge_cpu(frame_image, face_align_img, face_align_mask_img, face_swap_img, face_swap_mask_img, uni_mat):
    """Same as FaceMergerWorker._merge_on_cpu with GUI defaults (erode 5, blur 25, rct, bilinear, opacity 1)."""
    H, W = frame_image.shape[:2]
    frame_image = ImageProcessor(frame_image).to_ufloat32().get_image('HWC')
    face_mask = ImageProcessor(face_align_mask_img).to_ufloat32().get_image('HW')
    face_mask *= ImageProcessor(face_swap_mask_img).to_ufloat32().get_image('HW')
    face_mask = ImageProcessor(face_mask).erode_blur(5, 25, fade_to_border=True).get_image('HWC')
    frame_face_mask = ImageProcessor(face_mask).warp_affine(uni_mat, W, H).clip2((1.0 / 255.0), 0.0, 1.0, 1.0).get_image('HWC')
    face_swap_ip = ImageProcessor(face_swap_img).to_ufloat32()
    face_swap_ip.rct(like=face_align_img, mask=face_mask, like_mask=face_mask)
    frame_face_swap_img = face_swap_ip.warp_affine(uni_mat, W, H, interpolation=ImageProcessor.Interpolation.LINEAR).get_image('HWC')
    one_f = np.float32(1.0)
    return ne.evaluate('frame_image*(one_f-frame_face_mask) + frame_face_swap_img*frame_face_mask')


def merge_gpu(frame_image, face_align_img, face_align_mask_img, face_swap_img, face_swap_mask_img, uni_mat):
    """Same as FaceMergerWorker._merge_on_gpu (OpenCL) with GUI defaults."""
    H, W = frame_image.shape[:2]
    masks = [lib_cl.Tensor.from_value(face_align_mask_img), lib_cl.Tensor.from_value(face_swap_mask_img)]
    face_mask_t = lib_cl.any_wise("float X = (((float)I0) / 255.0)*(((float)I1) / 255.0); O = (X <= 0.5 ? 0 : 1);", *masks, dtype=np.uint8).transpose((2, 0, 1))
    face_mask_t = lib_cl.binary_morph(face_mask_t, 5, 25, fade_to_border=True, dtype=np.float32)
    face_swap_img_t = lib_cl.Tensor.from_value(face_swap_img).transpose((2, 0, 1), op_text='O = ((O_TYPE)I) / 255.0', dtype=np.float32)
    face_align_img_t = lib_cl.Tensor.from_value(face_align_img).transpose((2, 0, 1), op_text='O = ((O_TYPE)I) / 255.0', dtype=np.float32)
    face_swap_img_t = lib_cl.rct(face_swap_img_t, face_align_img_t, target_mask_t=face_mask_t, source_mask_t=face_mask_t)
    frame_face_mask_t = lib_cl.remap_np_affine(face_mask_t, uni_mat, interpolation=lib_cl.EInterpolation.LINEAR, output_size=(H, W), post_op_text='O = (O <= (1.0/255.0) ? 0.0 : O > 1.0 ? 1.0 : O);')
    frame_face_swap_img_t = lib_cl.remap_np_affine(face_swap_img_t, uni_mat, interpolation=lib_cl.EInterpolation.LINEAR, output_size=(H, W), post_op_text='O = clamp(O, 0.0, 1.0);')
    frame_image_t = lib_cl.Tensor.from_value(frame_image).transpose((2, 0, 1), op_text='O = ((float)I) / 255.0;', dtype=np.float32)
    frame_final_t = lib_cl.any_wise('O = I0*(1.0-I1) + I2*I1', frame_image_t, frame_face_mask_t, frame_face_swap_img_t, dtype=np.float32)
    return frame_final_t.transpose((1, 2, 0)).np()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dfm', required=True)
    p.add_argument('--input', required=True, help='video or image file')
    p.add_argument('--frames', type=int, default=300)
    p.add_argument('--out-dir', default=None)
    p.add_argument('--cpu', action='store_true', help='force CPUExecutionProvider')
    p.add_argument('--merge-gpu', action='store_true', help='merge on GPU via OpenCL (like FaceMerger device=GPU)')
    args = p.parse_args()

    import onnxruntime as ort
    print(f'onnxruntime {ort.__version__}, providers: {ort.get_available_providers()}')

    devices = lib_ort.get_available_devices_info(include_cpu=False)
    device = lib_ort.get_cpu_device_info() if (args.cpu or len(devices) == 0) else devices[0]
    print(f'device: {device}')

    merge_fn = merge_cpu
    if args.merge_gpu:
        cl_devices = lib_cl.get_available_devices_info()
        if len(cl_devices) == 0:
            raise Exception('No OpenCL device found')
        dev = lib_cl.get_device(cl_devices[0])
        dev.set_target_memory_usage(mb=512)
        lib_cl.set_default_device(dev)
        merge_fn = merge_gpu
        print(f'merge device (OpenCL): {cl_devices[0]}')

    t0 = time.perf_counter()
    detector = onnx_models.YoloV5Face(device)
    marker = onnx_models.FaceMesh(device)
    dfm = DFMModel(Path(args.dfm), device)
    print(f'models loaded in {time.perf_counter()-t0:.1f}s; DFM providers: {dfm._sess.get_providers()}, input {dfm.get_input_res()}')

    src = Path(args.input)
    is_image = src.suffix.lower() in ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
    cap = None if is_image else cv2.VideoCapture(str(src))
    still = cv2.imread(str(src)) if is_image else None

    out_dir = Path(args.out_dir) if args.out_dir else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    timings = {k: [] for k in ('detect', 'mark', 'align', 'swap', 'merge', 'total')}
    faces_found = 0
    n = 0
    warmup = 5
    writer = None
    while n < args.frames + warmup:
        if is_image:
            frame = still.copy()
        else:
            ok, frame = cap.read()
            if not ok:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ok, frame = cap.read()
                if not ok:
                    break
        H, W = frame.shape[:2]
        ts = time.perf_counter()

        rects = detector.extract(frame, threshold=0.5, fixed_window=480)[0]
        t1 = time.perf_counter()
        rects = FRect.sort_by_area_size([FRect.from_ltrb((l / W, t / H, r / W, b / H)) for l, t, r, b in rects])

        merged = frame
        tm = ta = tsw = tme = t1
        if len(rects) != 0:
            faces_found += 1
            face_urect = rects[0]
            face_image, face_uni_mat = face_urect.cut(frame, 1.4, 192)
            fh, fw = face_image.shape[:2]
            lmrks = marker.extract(face_image)[0]
            lmrks = lmrks[..., 0:2] / (fw, fh)
            face_ulmrks = FLandmarks2D.create(ELandmarks2D.L468, lmrks).transform(face_uni_mat, invert=True)
            tm = time.perf_counter()

            face_align_img, uni_mat = face_ulmrks.cut(frame, 2.2, 224, exclude_moving_parts=True, head_yaw=None,
                                                      x_offset=0, y_offset=-0.08, freeze_z_rotation=False)
            ta = time.perf_counter()

            celeb_face, celeb_mask, face_align_mask = dfm.convert(face_align_img, morph_factor=0.75)
            celeb_face, celeb_mask, face_align_mask = celeb_face[0], celeb_mask[0], face_align_mask[0]
            tsw = time.perf_counter()

            fah, faw = face_align_img.shape[:2]
            aligned_to_source_uni_mat = uni_mat.invert().to_exact_mat(faw, fah, W, H)
            merged = merge_fn(frame, face_align_img, face_align_mask, celeb_face, celeb_mask, aligned_to_source_uni_mat)
            merged = (np.clip(merged, 0, 1) * 255).astype(np.uint8)
            tme = time.perf_counter()

        if n >= warmup:
            timings['detect'].append(t1 - ts)
            timings['mark'].append(tm - t1)
            timings['align'].append(ta - tm)
            timings['swap'].append(tsw - ta)
            timings['merge'].append(tme - tsw)
            timings['total'].append(time.perf_counter() - ts)

            if out_dir is not None:
                if n == warmup + args.frames // 2:
                    cv2.imwrite(str(out_dir / 'frame_in.jpg'), frame)
                    cv2.imwrite(str(out_dir / 'frame_out.jpg'), merged)
                    if len(rects) != 0:
                        cv2.imwrite(str(out_dir / 'face_aligned.jpg'), face_align_img)
                        cv2.imwrite(str(out_dir / 'face_swapped.jpg'), celeb_face)
                if not is_image:
                    if writer is None:
                        writer = cv2.VideoWriter(str(out_dir / 'output.mp4'), cv2.VideoWriter_fourcc(*'mp4v'), 30, (W, H))
                    writer.write(merged)
        n += 1

    if writer is not None:
        writer.release()

    frames = len(timings['total'])
    print(f'\nframes: {frames} ({W}x{H}), frames with face: {faces_found}/{n}')
    for k, v in timings.items():
        v = np.array(v) * 1000
        print(f'  {k:7s} mean {v.mean():7.2f} ms   p95 {np.percentile(v, 95):7.2f} ms')
    total = np.array(timings['total'])
    print(f'\nFPS (serial, single process): {1.0 / total.mean():.1f}')


if __name__ == '__main__':
    main()
