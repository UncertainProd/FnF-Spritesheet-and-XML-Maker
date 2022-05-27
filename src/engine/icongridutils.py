from PIL import Image

def _icongrid_add_row(icongrid, iconsize=150):
    icongrid_cpy = icongrid.copy()
    new_icongrid = Image.new('RGBA', (icongrid_cpy.size[0], icongrid_cpy.size[1]+iconsize), (0, 0, 0, 0))
    new_icongrid.paste(icongrid_cpy)
    icongrid_cpy.close()
    return new_icongrid

def _get_last_row_and_col(icongrid, iconsize=150):
    _box = icongrid.getbbox()
    pix_to_index = lambda pixels: pixels//iconsize

    if _box:
        # finding last row index
        _, _, _, lastrow_y = _box
        last_row_index = pix_to_index(lastrow_y)
        
        # finding last col index
        _last_row_img = icongrid.crop((0, last_row_index*iconsize, icongrid.width, last_row_index*iconsize + iconsize))
        
        _box = _last_row_img.getbbox()
        if _box:
            _, _, lastcol_x, _ = _box
        else:
            print("ERROR: error in trying to find last column, setting to 0")
            lastcol_x = 0
        last_col_index = pix_to_index(lastcol_x)
    else:
        print("ERROR: icongrid is empty, cannot find bbox")
        last_row_index = 0
        last_col_index = 0
    
    return last_row_index, last_col_index

def appendIconToGrid(icongrid_path, iconpaths, iconsize=150):
    print("Icongrid from: {} \nIcons: {}".format(icongrid_path, len(iconpaths)))

    IMAGES_PER_COLUMN = 10
    icongrid = Image.open(icongrid_path)
    indices = []
    for iconpath in iconpaths:
        icon_img = Image.open(iconpath)

        # get location to paste it
        last_row_idx, last_col_idx = _get_last_row_and_col(icongrid)
        new_index = last_row_idx*IMAGES_PER_COLUMN + last_col_idx + 1
        indices.append(new_index)
        new_row_idx = new_index // IMAGES_PER_COLUMN
        new_col_idx = new_index % IMAGES_PER_COLUMN

        if new_row_idx * iconsize >= icongrid.height:
            print("Icongrid is full. Expanding it....")
            icongrid = _icongrid_add_row(icongrid)
        
        # paste image there
        # ...
        icongrid.paste(icon_img, (new_col_idx*iconsize, new_row_idx*iconsize))
    icongrid.save(icongrid_path)
    return 0, indices, None, None