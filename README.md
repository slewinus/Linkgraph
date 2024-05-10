
LINKTGRAPH

TO BUILD THE APP ON WINDOWS (verify to have the good path for the img and icons)
```bash
pyinstaller --onefile --windowed --name=linkgraph --icon="C:\Users\oscarr\Desktop\graph-creator\graph-creator\images\img.ico" --add-data "config.json;." --add-data "images/icon_app.png;images" main.py
   ```

    