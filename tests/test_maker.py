# -*- coding: utf-8 -*-

import pytest
from pibooth.pictures.factory import PilPictureFactory, OpenCvPictureFactory

footer_texts = ('This is the main title', 'Footer text 2', 'Footer text 3')
footer_fonts = ('Amatic-Bold', 'DancingScript-Regular', 'Roboto-LightItalic')
footer_colors = ((10, 0, 0), (0, 50, 0), (0, 50, 50))


def setup_factory(m, fond, overlay=''):
    m.add_text(footer_texts[0], footer_fonts[0], footer_colors[0], 'left')
    m.add_text(footer_texts[1], footer_fonts[1], footer_colors[1], 'center')
    m.add_text(footer_texts[2], footer_fonts[2], footer_colors[2], 'right')
    m.set_background(fond)
    if overlay:
        m.set_overlay(overlay)


def test_benchmark_pil_portrait(benchmark, captures_portrait, fond):
    factory = PilPictureFactory(2400, 3600, *captures_portrait)
    setup_factory(factory, fond)
    benchmark(factory.build)


def test_benchmark_pil_landscape(benchmark, captures_landscape, fond):
    factory = PilPictureFactory(3600, 2400, *captures_landscape)
    setup_factory(factory, fond)
    benchmark(factory.build)


def test_benchmark_cv2_portrait(benchmark, captures_portrait, fond):
    factory = OpenCvPictureFactory(2400, 3600, *captures_portrait)
    setup_factory(factory, fond)
    benchmark(factory.build)


def test_benchmark_cv2_landscape(benchmark, captures_landscape, fond):
    factory = OpenCvPictureFactory(3600, 2400, *captures_landscape)
    setup_factory(factory, fond)
    benchmark(factory.build)


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_cv2_portrait(captures_nbr, captures_portrait, fond):
    factory = OpenCvPictureFactory(2400, 3600, *captures_portrait[:captures_nbr])
    setup_factory(factory, fond)
    factory.save("OpenCV-portrait-{}.jpg".format(captures_nbr))


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_cv2_landscape(captures_nbr, captures_landscape, fond):
    factory = OpenCvPictureFactory(3600, 2400, *captures_landscape[:captures_nbr])
    setup_factory(factory, fond)
    factory.save("OpenCV-landscape-{}.jpg".format(captures_nbr))


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_pil_portrait(captures_nbr, captures_portrait, fond):
    factory = PilPictureFactory(2400, 3600, *captures_portrait[:captures_nbr])
    setup_factory(factory, fond)
    factory.save("PIL-portrait-{}.jpg".format(captures_nbr))


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_pil_landscape(captures_nbr, captures_landscape, fond):
    factory = PilPictureFactory(3600, 2400, *captures_landscape[:captures_nbr])
    setup_factory(factory, fond)
    factory.save("PIL-landscape-{}.jpg".format(captures_nbr))


def test_save_pil_overlay(captures_landscape, fond, overlay):
    factory = PilPictureFactory(3600, 2400, *captures_landscape)
    setup_factory(factory, fond, overlay)
    factory.save("PIL-overlay-4.jpg")


def test_save_cv2_overlay(captures_landscape, fond, overlay):
    factory = OpenCvPictureFactory(3600, 2400, *captures_landscape)
    setup_factory(factory, fond, overlay)
    factory.save("OpenCV-overlay-4.jpg")
