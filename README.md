

Cache:

- Use **relative path** `bbase_dir` with not extensions.
- **Cache assets by groups**. Keep in cache those assets while at least one of the gorups is still in use: for example get_image("enemies/ghost", group="level3") -> Ghosts loaded if unload cacche for enemies/ghost.
- **Lazy load**: If any image is not in any group, is added to *"default"* group.
- **Scaled copies**: get_image(name, scale) create a scaled copy from cached, not from disk.
- **Optimize for frames**: repeat calls to get_image is a couple of dictionary lookups for calls inside `draw()`.
- **Fast opaque imgs**: When `alpha=false` use convert() instead convert_alpha().
- **LOdaing Screens**: Option to use loadind screens by `iter_load_group()` yields (done, total) for draw even a proggress bar.
- **Extension case insensitive**: Just don't care if a file is .png or .PNG.
- **Default elements instead originals**: If load fails, use default values.





- [Render tiles](https://pygame.readthedocs.io/en/latest/tiles/tiles.html)      - How to render tiles map.
- [Key map](https://www.pygame.org/docs/ref/key.html)       - Pygame keymap.
- [cache structure](https://stackoverflow.com/questions/17615447/pre-loading-images-pygame)         - Managing cache images for pygame.
- [Read all files](https://realpython.com/get-all-files-in-directory-python/)          - How to read all files by using python.
- [Optimisation for Pygame](https://bugnet.io/blog/pygame-performance-tips-for-indie-developers)        - Tips to improve the performance.