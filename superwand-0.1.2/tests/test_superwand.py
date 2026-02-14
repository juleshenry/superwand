r"""
                                ▂▃▃▃▄▄▄▄▃▂▃▃▂▁
                                ███████▇▃ ▅██▆
                                ▅██████▇▅▁███▃
                                ▄██████▇▃▁██▆▁
                                ▁▇██████▅▃██▅
                             ▁▃  ▇█████▆ ▁██▅ ▁▃▁
                             ███▆▇█████▆▁▁▇█▇▅██▇
                             ▇█████▇▇▇█▇▄▄▇▇▆███▅
                             ▁▃▇██████████████▆▂
                               ▁▁▅██▇▆▇▁▆▇▅█▆▁
                                 ▁▆█▂ ▇▁▁ ▁▆▁
                                  ▃█▇▆▆▇▅▅▇█▃
                               ▁▂▅▇▆▇▇▅▆▅▇▃▆▃▅▃▁
                           ▁▂▄▆▅▃▁▃▆▂▂▄▄▂▁▁▆ ▁▃▆█▆▅▃▁
                          ▂███▆▂  ▁▂▄▃▃▂▂▃▁▅  ▁▄█████▄
                         ▁▇███▅▃▁          ▅  ▂▄▇█████▄▁
                         ▄████▅▁  ▃▁       ▅   ▂███████▂
                         ██████▄  ▄▁       ▅  ▂████████▇▁
                        ▅███████▁ ▃▁  ▂    ▆ ▁▆█████████▄
                       ▂████████▆▁▄▁  ▁   ▁▆▁▆███████████▁
                       ▇█████████▅▄▂▁▁▂▁▂▂▄▆▂████████████▆
                      ▄██████████▆▆█▅▆▆▄▃▃▅▇█████▇▅███████▃
                     ▁██████████████▇▇▅▂ ▁▄██████▇▂████████▁
                    ▁▄▅▄▅▇██▇██████▇▄▆▅▂  ▃███████▃▅█████▇▇▅▁
                    ▂▃    ▂█▆▇████████▆▃ ▁▅███████▄▁██▅▂▁  ▁▄▁
                    ▅▂▂▁▁▁▁▅▁▇██████████▇▆█████████▁▃▆    ▁▂▂▅
                    ▃▃▁▁▆▄▆▅▄██████████████████████▁ ▅▃▂▃▃▃▆▅▂
                   ▂▅▂▄▇▇▆▃ ▂██████████████████████▁ ▁▃▃▆▃▁▂▅▁
                   █▅ ▆▇▆   ▂██████████████████████▁    ▄▁▄▁▁▄
                 ▁▃██▂▅▅▃   ▂██████████████████████▁   ▁▅▄▂▇▁▅
               ▂▅▇▅▃▄▃▂     ▂██████████████████████▁   ▁▃▄▅▇▃▄
            ▁▃▆▆▃▁          ▁██████████████████████▁     ▁▅▅▂
          ▂▄▇▅▁             ▁██████████████████████▁
        ▁▂▆▃▁               ▁██████████▇███████████▁
     ▁▁▁▁▁                  ▁▅█████████▂▄██████████▁
   ▁▁▂▁▁                     ▃█████████▁▃▇█████████▁
▂▁▂▂▁                        ▃█████████▁ ▄█████████
▁▂▁                          ▁▅███████▆  ▃████████▃
                              ▃██████▇▁   ▇███████▂
                               ██████▇    ▁██████▇▂
                               ▂█████▃     ▇█████▁
                               ▂█████▂     ▄█████▁
                              ▂██████▄     ▄█████▆▁
                            ▁▄██████▆▃     ▃██████▇▂
                           ▁█████▆▂▁        ▁▂▅█████▅▁
                            ▂▂▂▂▁              ▁▄▅▇▇▇▂


                                                                     ||`
                                                                     ||
('''' '||  ||` '||''|, .|''|, '||''| '\\    //`  '''|.  `||''|,  .|''||
 `'')  ||  ||   ||  || ||..||  ||      \\/\//   .|''||   ||  ||  ||  ||
`...'  `|..'|.  ||..|' `|...  .||.      \/\/    `|..||. .||  ||. `|..||.
                ||
               .||
                           by Julian Henry
"""

import pytest
from unittest.mock import patch, MagicMock
from superwand.core.superwand import SuperWand
from superwand.core.themes import color_themes
from superwand.utils.gradients import clamp


def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(15, 0, 10) == 10


def test_superwand_init():
    sw = SuperWand(color_themes, 8)
    assert sw.color_themes == color_themes
    assert sw.number == 8


@patch("superwand.core.superwand.np_get_prominent_regions")
@patch("superwand.core.superwand.np_inject_theme")
def test_apply_theme_to_image(mock_inject, mock_get_regions):
    sw = SuperWand(color_themes, 8)
    mock_get_regions.return_value = {"region1": "data"}

    # Test with specific theme
    sw.apply_theme_to_image("dummy.png", "Tropical")

    mock_get_regions.assert_called_with("dummy.png", number=8, tolerance=50)
    mock_inject.assert_called_once()
    args, kwargs = mock_inject.call_args
    assert args[0] == {"region1": "data"}
    assert args[1] == "Tropical"
    assert args[2] == "dummy.png"
    assert kwargs["number"] == 8


@patch("superwand.core.superwand.np_get_prominent_regions")
@patch("superwand.core.superwand.np_inject_theme")
def test_apply_theme_to_image_all_themes(mock_inject, mock_get_regions):
    sw = SuperWand({"Theme1": [], "Theme2": []}, 8)
    mock_get_regions.return_value = {"region1": "data"}

    # Test without specific theme (should apply all)
    sw.apply_theme_to_image("dummy.png", None)

    assert mock_inject.call_count == 2
    # Check calls
    calls = mock_inject.call_args_list
    themes_called = [call[0][1] for call in calls]
    assert "Theme1" in themes_called
    assert "Theme2" in themes_called


@patch("superwand.core.superwand.np_get_prominent_regions")
@patch("superwand.core.superwand.np_inject_theme")
def test_apply_all_themes_to_image(mock_inject, mock_get_regions):
    # This method in SuperWand seems to iterate themes and call get_regions inside the loop?
    # Let's check the implementation of apply_all_themes_to_image in superwand.py
    # def apply_all_themes_to_image(self, img_path):
    #     for theme_name in self.color_themes:
    #         color_pix_dict = np_get_prominent_regions(img_path)
    #         np_inject_theme(color_pix_dict, theme_name, img_path)

    sw = SuperWand({"Theme1": [], "Theme2": []}, 8)
    mock_get_regions.return_value = {"region1": "data"}

    sw.apply_all_themes_to_image("dummy.png")

    assert mock_get_regions.call_count == 1
    assert mock_inject.call_count == 2


@patch("superwand.core.superwand.SuperWand")
@patch("argparse.ArgumentParser.parse_args")
def test_main(mock_parse_args, mock_superwand_class):
    from superwand.core.superwand import main

    # Setup mocks
    mock_args = MagicMock()
    mock_args.image_path = "test.png"
    mock_args.theme = "Tropical"
    mock_parse_args.return_value = mock_args

    mock_sw_instance = mock_superwand_class.return_value

    # Run main
    main()

    # Verify
    mock_superwand_class.assert_called_once()
    # Check that apply_theme_to_image was called with correct arguments
    called_args, called_kwargs = mock_sw_instance.apply_theme_to_image.call_args
    assert called_args == ("test.png", "Tropical")
