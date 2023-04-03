## The Video Editor's Render Script for Blender 3.x
 
Based on [*mikeycal*'s script](https://github.com/mikeycal/the-video-editors-render-script-for-blender).

Modifications:
- Works with Blender 3.x
- More intuitive &amp; predictive output files
- No more `_Click_to_Render_` scripts.
- Smoothen file/folder overwriting experience.

To get the script:

```bash
git get https://github.com/b1f6c1c4/the-video-editors-render-script-for-blender/blob/master/video_editors_render_script.py
```

### Recommended way of using the script:

<details>
<summary>Dead simple, one-line solution of multicore rendering</summary>

1. In your Blender, set Scene Properties:
   * File Format: `FFmpeg Video`
   * Encoding:
      * Container: `Matroska`
   * Video:
      * Video Codec: `WebM/VP9` or `AV1` or `H.264`
      * Output Quality: Anything *OTHER THAN* `Lossless`
      * Encoding Speed: (adjust accordingly)
   * Audio:
      * Audio Codec: `AAC` or `Vorbis`
      * Bitrate: 192

2. Invoke the script:

    ```bash
    blender -b <path-to-your-.blend> -P <path-to-video_editors_render_script.py>
    ```

3. Verify that, in the same folder as `.blend`, `**-video.avi` exists.
</details>

<details>
<summary>I have a long video, and I want to FFmpeg myself</summary>

1. In your Blender, set Scene Properties:
    * File Format: `FFmpeg Video`
    * Encoding:
        * Container: AVI
    * Video:
        * Video Codec: H.264
        * Output Quality: Lossless
    * Audio:
        * Audio Codec: PCM

2. _(Optional)_ `ssfhs` or NFS mount `.blend` file as well as media files

3. Invoke the script:

    ```bash
    blender -b <path-to-your-.blend> -P <path-to-video_editors_render_script.py>
    ```

4. Verify that, in the same folder as `.blend`, `**-video.avi` exists.
5. Invoke ffmpeg to compress as will:

   - E.g. HEVC/AAC on MKV, using nVidia CUDA hardware acceleration:

      ```bash
      ffmpeg -i <path>-video.avi \
          -c:v hevc_nvenc -crf 18 -c:a aac -b:a 128k \
          <output.mkv>
      ```
</details>

<details>
<summary>I have extremely large memory &amp; disk space</summary>

**Requirement:**
Your video is very short, and both `/tmp` and output dir (same dir as `.blend`) are very large.
We need 400MB / second / 1080p60.
Preferably, `/tmp` is tmpfs, and your disk has very high R/W speed.

1. In your Blender, set Scene Properties / File Format to `AVI Raw`

2. _(Optional)_ `ssfhs` or NFS mount `.blend` file as well as media files

3. Invoke the script:

    ```bash
    blender -b <path-to-your-.blend> -P <path-to-video_editors_render_script.py>
    ```

4. Verify that, in the same folder as `.blend`, `**-audio.pcm` and `**-video.avi` exist.
5. Invoke ffmpeg to compress as will:

    - E.g. HEVC/AAC on MKV, using nVidia CUDA hardware acceleration:

       ```bash
       ffmpeg -i <path>-video.avi -i <path>-audio.pcm \
           -c:v hevc_nvenc -crf 18 -c:a aac -b:a 128k \
           -map 0:v:0 -map 1:a:0 \
           <output.mkv> -async 1
       ```
</details>

<details>
<summary>I want to inspect individual frames</summary>

**Requirement:**
Your video is short, and output dir (same as `.blend` or another one) is large.
We need 150MB / second / 1080p60.

1. In your Blender, set Scene Properties / File Format to `PNG`, Compression to `15%`

2. _(Optional)_ `ssfhs` or NFS mount `.blend` file as well as media files
3. _(Optional)_ Create a separate directory for writing output files (150MB/second/1080p60), and:

    ```bash
    ln -s /<path>/<to>/<out-dir> <path>-seq/
    ```

4. Invoke the script:

    ```bash
    blender -b <path-to-your-.blend> -P <path-to-video_editors_render_script.py>
    ```

5. Verify that, in the same folder as `.blend`, `**-audio.pcm` and `**-seq/` exist.
6. Invoke ffmpeg to compress as will:

   - E.g. HEVC/AAC on MKV, using nVidia CUDA hardware acceleration:

      ```bash
      ffmpeg -i <path>-seq/%04d.png -i <path>-audio.pcm \
          -c:v hevc_nvenc -crf 18 -c:a aac -b:a 128k \
          -map 0:v:0 -map 1:a:0 \
          <output.mkv> -async 1
      ```
</details>

### Legal

GPL v3
