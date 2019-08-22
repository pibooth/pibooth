# -*- coding: utf-8 -*-

import pytest
from pibooth.pictures.maker import PilPictureMaker, OpenCvPictureMaker

footer_texts = ('This is the main title', 'Footer text 2', 'Footer text 3')
footer_fonts = ('Amatic-Bold', 'DancingScript-Regular', 'Roboto-LightItalic')
footer_colors = ((10, 0, 0), (0, 50, 0), (0, 50, 50))


def setup_maker(m, fond):
    m.add_text(footer_texts[0], footer_fonts[0], footer_colors[0], 'left')
    m.add_text(footer_texts[1], footer_fonts[1], footer_colors[1], 'center')
    m.add_text(footer_texts[2], footer_fonts[2], footer_colors[2], 'right')
    m.set_background(fond)


def test_benchmark_pil_portrait(benchmark, captures_portrait, fond):
    maker = PilPictureMaker(2400, 3600, *captures_portrait)
    setup_maker(maker, fond)
    benchmark(maker.build)


def test_benchmark_pil_landscape(benchmark, captures_landscape, fond):
    maker = PilPictureMaker(3600, 2400, *captures_landscape)
    setup_maker(maker, fond)
    benchmark(maker.build)


def test_benchmark_cv2_portrait(benchmark, captures_portrait, fond):
    maker = OpenCvPictureMaker(2400, 3600, *captures_portrait)
    setup_maker(maker, fond)
    benchmark(maker.build)


def test_benchmark_cv2_landscape(benchmark, captures_landscape, fond):
    maker = OpenCvPictureMaker(3600, 2400, *captures_landscape)
    setup_maker(maker, fond)
    benchmark(maker.build)


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_cv2_portrait(captures_nbr, captures_portrait, fond):
    maker = OpenCvPictureMaker(2400, 3600, *captures_portrait[:captures_nbr])
    setup_maker(maker, fond)
    maker.save("OpenCV-portrait-{}.jpg".format(captures_nbr))


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_cv2_landscape(captures_nbr, captures_landscape, fond):
    maker = OpenCvPictureMaker(3600, 2400, *captures_landscape[:captures_nbr])
    setup_maker(maker, fond)
    maker.save("OpenCV-landscape-{}.jpg".format(captures_nbr))


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_pil_portrait(captures_nbr, captures_portrait, fond):
    maker = PilPictureMaker(2400, 3600, *captures_portrait[:captures_nbr])
    setup_maker(maker, fond)
    maker.save("PIL-portrait-{}.jpg".format(captures_nbr))


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_pil_landscape(captures_nbr, captures_landscape, fond):
    maker = PilPictureMaker(3600, 2400, *captures_landscape[:captures_nbr])
    setup_maker(maker, fond)
    maker.save("PIL-landscape-{}.jpg".format(captures_nbr))
