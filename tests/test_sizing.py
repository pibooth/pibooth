# -*- coding: utf-8 -*-


from pibooth.pictures import sizing


def test_resize_original_small_inner():
    size = sizing.new_size_keep_aspect_ratio((600, 200), (900, 600))
    assert size == (900, 300)


def test_resize_original_small_outer():
    size = sizing.new_size_keep_aspect_ratio((600, 200), (900, 600), 'outer')
    assert size == (1800, 600)


def test_resize_original_big_inner():
    size = sizing.new_size_keep_aspect_ratio((1000, 1200), (800, 600))
    assert size == (500, 600)


def test_resize_original_big_outer():
    size = sizing.new_size_keep_aspect_ratio((1000, 1200), (800, 600), 'outer')
    assert size == (800, 960)


def test_crop_original_small_left():
    coordinates = sizing.new_size_by_croping((600, 200), (900, 600), 'top-left')
    assert coordinates == (0, 0, 900, 600)


def test_crop_original_small_middle():
    coordinates = sizing.new_size_by_croping((600, 200), (900, 600))
    assert coordinates == (-150, -200, 750, 400)


def test_crop_original_big_topleft():
    coordinates = sizing.new_size_by_croping((1000, 1200), (800, 600), 'top-left')
    assert coordinates == (0, 0, 800, 600)


def test_crop_original_big_middle():
    coordinates = sizing.new_size_by_croping((1000, 1200), (800, 600))
    assert coordinates == (100, 300, 900, 900)


def test_crop_ratio_original_small_left():
    coordinates = sizing.new_size_by_croping_ratio((600, 200), (900, 600), 'top-left')
    assert coordinates == (0, 0, 300, 200)


def test_crop_ratio_original_small_middle():
    coordinates = sizing.new_size_by_croping_ratio((600, 200), (900, 600))
    assert coordinates == (150, 0, 450, 200)


def test_crop_ratio_original_big_topleft():
    coordinates = sizing.new_size_by_croping_ratio((1000, 1200), (800, 600), 'top-left')
    assert coordinates == (0, 0, 1000, 750)


def test_crop_ratio_original_big_middle():
    coordinates = sizing.new_size_by_croping_ratio((1000, 1200), (800, 600))
    assert coordinates == (0, 225, 1000, 975)
