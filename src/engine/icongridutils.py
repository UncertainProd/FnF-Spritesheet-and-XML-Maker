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

ICON_PERFECT_FIT = 0
ICON_BIGGER_THAN_AREA = 1
ICON_SMALLER_THAN_AREA = 2

def _check_icon_size(icon, check_width=150, check_height=150):
    # 0 = icon is 150x150
    # 1 = icon is too wide/tall
    # 2 = icon is smaller than 150x150 area
    if icon.width == check_width and icon.height == check_height:
        return ICON_PERFECT_FIT
    elif icon.width > 150 or icon.height > 150:
        return ICON_BIGGER_THAN_AREA
    else:
        return ICON_SMALLER_THAN_AREA

def _center_icon(icon):
    w, h = icon.size
    final_icon = Image.new('RGBA', (150, 150), (0, 0, 0, 0))
    dx = (150 - w) // 2
    dy = (150 - h) // 2
    final_icon.paste(icon, (dx, dy))
    return final_icon

def appendIconToGrid(icongrid_path, iconpaths, iconsize=150):
    print("Icongrid from: {} \nIcons: {}".format(icongrid_path, len(iconpaths)))

    return_status = 0
    indices = []
    problem_icon = None
    exception_msg = None

    IMAGES_PER_COLUMN = 10

    try:
        # icongrid = Image.open(icongrid_path)
        with Image.open(icongrid_path).convert('RGBA') as icongrid:
            # icongrid = icongrid.convert('RGBA')
            for iconpath in iconpaths:
                # icon_img = Image.open(iconpath)
                with Image.open(iconpath).convert('RGBA') as icon_img:
                    # check if icon_img is 150x150
                    can_fit = _check_icon_size(icon_img)
                    if can_fit == ICON_BIGGER_THAN_AREA:
                        # if the icon is too big, ignore it (for now)
                        return_status = 2
                        problem_icon = iconpath
                        continue
                    elif can_fit == ICON_SMALLER_THAN_AREA:
                        print(f"Icon: {iconpath} is smaller than 150x150, centering it....")
                        icon_img = _center_icon(icon_img)

                    # get location to paste it
                    last_row_idx, last_col_idx = _get_last_row_and_col(icongrid)
                    
                    new_index = last_row_idx*IMAGES_PER_COLUMN + last_col_idx + 1
                    indices.append(new_index)
                    new_row_idx = new_index // IMAGES_PER_COLUMN
                    new_col_idx = new_index % IMAGES_PER_COLUMN

                    if new_row_idx * iconsize >= icongrid.height:
                        print("Icongrid is full. Expanding it....")
                        icongrid = _icongrid_add_row(icongrid)
                    
                    icongrid.paste(icon_img, (new_col_idx*iconsize, new_row_idx*iconsize))
            icongrid.save(icongrid_path)
    except Exception as e:
        return_status = -1
        exception_msg = f"{e.__class__.__name__} : {str(e)}"


    return return_status, indices, problem_icon, exception_msg

def makePsychEngineIconGrid(iconpaths, savepath, img_size=150):
    # this function works for any number of icons that you provide, even though psych engine uses 2 icons for a character
    status = 0
    problemimg = None
    exception_msg = None

    good_icons = []
    for iconpath in iconpaths:
        try:
            icon = Image.open(iconpath).convert('RGBA')
        except Exception as e:
            exception_msg = f"{e.__class__.__name__} : {str(e)}"
            continue
        fit_status = _check_icon_size(icon)
        if fit_status == ICON_BIGGER_THAN_AREA:
            problemimg = iconpath
            status = 1
            icon.close()
            continue
        elif fit_status == ICON_SMALLER_THAN_AREA:
            print(f"Icon: {iconpath} is smaller than 150x150, centering it....")
            icon = _center_icon(icon)
        good_icons.append(icon)
    
    if len(good_icons) == 0:
        return 1, problemimg, exception_msg

    final_icongrid = Image.new('RGBA', (img_size*len(good_icons), img_size), (0, 0, 0, 0))
    for i, icon in enumerate(good_icons):
        final_icongrid.paste(icon, (i*img_size, 0))
        icon.close()
    
    final_icongrid.save(savepath)
    final_icongrid.close()

    return status, problemimg, exception_msg