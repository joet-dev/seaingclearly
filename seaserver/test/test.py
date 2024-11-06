from ..processing import process_img


process_img(
    None,
    None,
    {
        "adaptive_histograph_equalisation": True,
        "richard_lucy_deconvolution": True,
        "super_res_upscale": True,
        "white_balance": True,
    },
)
