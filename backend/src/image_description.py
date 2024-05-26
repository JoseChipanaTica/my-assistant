import base64


def image_description(frame_bytes):
    base64_bytes = base64.b64encode(frame_bytes)
    base64_string = base64_bytes.decode('utf-8')

    return {"role": "user", "content": [{"type": "image_url", "image_url": {
        "url": f'data:image/jpg;base64,{base64_string}', "detail": "low"}}]}
