import asyncio
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import freeze_support
import os

from tqdm import tqdm

from ffapi.ff import get_client_session
from rest_api.db import select
from rest_api.requests import fetch_many
from toloka.interface.task import Task
from toloka.interface.toloka import Toloka


PATH_FACE = "C:/Users/Somov.A/YandexDisk-a.somov.homemarket@yandex.ru/Приложения/Яндекс.Толока/face-matching/faces/"
PATH_FRAME = "C:/Users/Somov.A/YandexDisk-a.somov.homemarket@yandex.ru/Приложения/Яндекс.Толока/face-matching/frames/"
PATH_FRAME_SRC = "C:/Users/Somov.A/Desktop/Src/"


def convert_frame(id, path_src, path_dest, coords):
    left, right, top, bottom = coords
    with open(path_src + f'{id}.jpeg', 'rb') as f:
        photo = f.read()
    image = BytesIO(photo)
    source_img = Image.open(image)
    draw = ImageDraw.Draw(source_img)
    draw.rectangle(((left - 7, top - 7), (right + 7, bottom + 7)), outline="green", width=7)
    w, h = source_img.size
    crop_width = (right - left) * 3
    upper_crop = (bottom - top) * 2
    source_img = source_img.crop((max(left - crop_width, 0), max(top - upper_crop, 0), min(right + crop_width, w), h))
    source_img.save(path_dest + f'{id}.jpeg', "JPEG")


def save_photos(photos, path, ext, optimize_quality, overwrite=False):
    for id, photo in photos:
        filename = path + str(id) + ext
        if not overwrite and os.path.isfile(filename):
            continue
        else:
            source_img = Image.open(photo)
            if optimize_quality:
                source_img.save(filename, "JPEG", optimize=True, quality=80)
            else:
                source_img.save(filename, "JPEG")


async def load_and_save(urls, url_to_id, path, ext, optimize_quality, overwrite=False):
    async for batch in fetch_many(get_client_session, urls, path=None):
        photos = [(url_to_id[url], photo) for url, photo in batch]
        executor.submit(save_photos, photos, path, ext, optimize_quality, overwrite)


async def main():
    async with Toloka.init_session():
        result = await Task.list_all(pool_id=Toloka.pool_id)
    frame_ids = set()
    face_ids = set()
    for i in result:
        iv = i['input_values']
        frame_ids.add(int(iv['image_left'].split('.')[0]))
        frame_ids.add(int(iv['image_right'].split('.')[0]))
        face_ids.add(int(iv['thumb_left1'].split('.')[0]))
        face_ids.add(int(iv['thumb_left2'].split('.')[0]))
        face_ids.add(int(iv['thumb_left3'].split('.')[0]))
        face_ids.add(int(iv['thumb_right1'].split('.')[0]))
        face_ids.add(int(iv['thumb_right2'].split('.')[0]))
        face_ids.add(int(iv['thumb_right3'].split('.')[0]))
    rows = select("""
            SELECT
                Id,
                REPLACE(Face, '195.9.164.86', '84.253.104.198') Face,
                REPLACE(Frame, '195.9.164.86', '84.253.104.198') Frame,
                FrameCoordsLeft,
                FrameCoordsRight,
                FrameCoordsTop,
                FrameCoordsBottom
            FROM FindFaceEvents WITH (nolock)
        """,
        return_columns=False
    )
    frame_urls = [(id, frame) for id, face, frame, *_ in rows if id in frame_ids]
    face_urls = [(id, face) for id, face, frame, *_ in rows if id in face_ids]
    url_to_id = {url: id for id, url in frame_urls + face_urls}

    existing_faces = [int(x.split('.')[0]) for x in os.listdir(PATH_FACE)]
    existing_frames = [int(x.split('.')[0]) for x in os.listdir(PATH_FRAME)]
    loaded_frames = os.listdir(PATH_FRAME_SRC)

    frames_to_load = [frame for id, frame in frame_urls
                            if frame.split('/')[-1] not in loaded_frames
                            and id not in existing_frames]
    faces_to_load = [face for id, face in face_urls if id not in existing_faces]
    # input('Start?')
    r_faces = asyncio.create_task(load_and_save(faces_to_load, url_to_id, PATH_FACE, 'jpg', False, False))
    r_frames = asyncio.create_task(load_and_save(frames_to_load, url_to_id, PATH_FRAME_SRC, 'jpeg', True, False))
    for task in asyncio.as_completed([r_faces, r_frames]):
        await task

    id_to_coords = {id: coords for id, face, frame, *coords in rows}
    frames_to_reformat = [(id, id_to_coords[id])
                          for id, frame in frame_urls
                          if id not in existing_frames]
    for id, coords in tqdm(frames_to_reformat, desc='Transforming frames'):
        convert_frame(id, PATH_FRAME_SRC, PATH_FRAME, coords)


def delete_non_numeric_faces():
    res = []
    for f in os.listdir(PATH_FACE):
        if not f.split('.')[0].isdigit():
            os.remove(PATH_FACE + f)
            res.append(f)
    print(len(res))


def rename_src_frames():
    rows = select("""
            SELECT
                Id,
                REPLACE(Frame, '195.9.164.86', '84.253.104.198') Frame
            FROM FindFaceEvents WITH (nolock)
        """,
        return_columns=False
    )
    url_name_to_id = {frame.split('/')[-1]: id for id, frame in rows}
    res = []
    for f in tqdm(os.listdir(PATH_FRAME_SRC)):
        if not f.split('.')[0].isdigit():
            os.rename(PATH_FRAME_SRC + f, PATH_FRAME_SRC + str(url_name_to_id[f]) + '.jpeg')
            res.append(f)
    print(len(res))


def test_uniqness_of_ids():
    rows = select("""
            SELECT
                Id,
                REPLACE(Face, '195.9.164.86', '84.253.104.198') Face,
                REPLACE(Frame, '195.9.164.86', '84.253.104.198') Frame,
                FrameCoordsLeft,
                FrameCoordsRight,
                FrameCoordsTop,
                FrameCoordsBottom
            FROM FindFaceEvents WITH (nolock)
        """,
        return_columns=False
    )
    frame_urls = [(id, frame) for id, face, frame, *_ in rows]
    face_urls = [(id, face) for id, face, frame, *_ in rows]
    url_to_id = {url: id for id, url in frame_urls + face_urls}
    assert len(set(frame_urls)) == len(frame_urls)
    assert len(set(face_urls)) == len(face_urls)
    assert len(set([url.split('/')[-1] for id, url in frame_urls])) == len(set(frame_urls))
    assert len(set([url.split('/')[-1] for id, url in face_urls])) == len(set(face_urls))


if __name__ == '__main__':
    freeze_support()
    with ProcessPoolExecutor() as executor:
        asyncio.run(main())
