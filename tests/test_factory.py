# -*- coding: utf-8 -*-

import pytest
from pibooth.pictures.factory import PilPictureFactory, OpenCvPictureFactory

footer_texts = ('This is the main title', 'Footer text 2', 'Footer text 3')
footer_fonts = ('Amatic-Bold', 'DancingScript-Regular', 'Roboto-LightItalic')
footer_colors = ((10, 0, 0), (0, 50, 0), (0, 50, 50))


def setup_factory(m, fond_path, overlay=''):
    m.add_text(footer_texts[0], footer_fonts[0], footer_colors[0], 'left')
    m.add_text(footer_texts[1], footer_fonts[1], footer_colors[1], 'center')
    m.add_text(footer_texts[2], footer_fonts[2], footer_colors[2], 'right')
    m.set_background(fond_path)
    if overlay:
        m.set_overlay(overlay)


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_cv2_portrait(captures_nbr, captures_portrait, fond_path, tmpdir):
    factory = OpenCvPictureFactory(2400, 3600, *captures_portrait[:captures_nbr])
    setup_factory(factory, fond_path)
    path = tmpdir.join("OpenCV-portrait-{}.jpg".format(captures_nbr))
    factory.save(str(path))


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_cv2_landscape(captures_nbr, captures_landscape, fond_path, tmpdir):
    factory = OpenCvPictureFactory(3600, 2400, *captures_landscape[:captures_nbr])
    setup_factory(factory, fond_path)
    path = tmpdir.join("OpenCV-landscape-{}.jpg".format(captures_nbr))
    factory.save(str(path))


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_pil_portrait(captures_nbr, captures_portrait, fond_path, tmpdir):
    factory = PilPictureFactory(2400, 3600, *captures_portrait[:captures_nbr])
    setup_factory(factory, fond_path)
    path = tmpdir.join("PIL-portrait-{}.jpg".format(captures_nbr))
    factory.save(str(path))


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_pil_landscape(captures_nbr, captures_landscape, fond_path, tmpdir):
    factory = PilPictureFactory(3600, 2400, *captures_landscape[:captures_nbr])
    setup_factory(factory, fond_path)
    path = tmpdir.join("PIL-landscape-{}.jpg".format(captures_nbr))
    factory.save(str(path))


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_pil_overlay_portrait(captures_nbr, captures_portrait, fond_path, overlays_portrait_path, tmpdir):
    factory = PilPictureFactory(2400, 3600, *captures_portrait[:captures_nbr])
    setup_factory(factory, fond_path, overlays_portrait_path[captures_nbr - 1])
    path = tmpdir.join("PIL-portrait-overlay-{}.jpg".format(captures_nbr))
    factory.save(str(path))


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_pil_overlay_landscape(captures_nbr, captures_landscape, fond_path, overlays_landscape_path, tmpdir):
    factory = PilPictureFactory(3600, 2400, *captures_landscape[:captures_nbr])
    setup_factory(factory, fond_path, overlays_landscape_path[captures_nbr - 1])
    path = tmpdir.join("PIL-landscape-overlay-{}.jpg".format(captures_nbr))
    factory.save(str(path))


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_cv2_overlay_portrait(captures_nbr, captures_portrait, fond_path, overlays_portrait_path, tmpdir):
    factory = OpenCvPictureFactory(2400, 3600, *captures_portrait[:captures_nbr])
    setup_factory(factory, fond_path, overlays_portrait_path[captures_nbr - 1])
    path = tmpdir.join("OpenCV-portrait-overlay-{}.jpg".format(captures_nbr))
    factory.save(str(path))


@pytest.mark.parametrize('captures_nbr', [1, 2, 3, 4])
def test_save_cv2_overlay_landscape(captures_nbr, captures_landscape, fond_path, overlays_landscape_path, tmpdir):
    factory = OpenCvPictureFactory(3600, 2400, *captures_landscape[:captures_nbr])
    setup_factory(factory, fond_path, overlays_landscape_path[captures_nbr - 1])
    path = tmpdir.join("OpenCV-landscape-overlay-{}.jpg".format(captures_nbr))
    factory.save(str(path))
