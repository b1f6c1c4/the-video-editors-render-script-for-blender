## The Video Editor's Render Script for Blender 3.x
 
Based on [*mikeycal*'s script](https://github.com/mikeycal/the-video-editors-render-script-for-blender).

Modifications:
- Only Linux officially supported.
- Works with Blender 3.x
- More intuitive output files
- Separate Video and Audio (so you can manually call ffmpeg)
- _WIP_ Render over ssh
- No more `_Click_to_Render_` thing.

### Recommended workflow 1: 

1. Get the script:

    ```bash
    git get https://github.com/b1f6c1c4/the-video-editors-render-script-for-blender/blob/master/video_editors_render_script.py
    ```
   
2. In your Blender, set Scene Properties / File Format to `AVI Raw`

3. _(Optional)_ `ssfhs` or NFS mount `.blend` file as well as media files

4. Invoke the script:

   ```bash
   blender -b <path-to-your-.blend> -P <path-to-video_editors_render_script.py>
   ```

### Legal

GPL v3
