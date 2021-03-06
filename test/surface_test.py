if __name__ == '__main__':
    import sys
    import os
    pkg_dir = os.path.split(os.path.abspath(__file__))[0]
    parent_dir, pkg_name = os.path.split(pkg_dir)
    is_pygame_pkg = (pkg_name == 'tests' and
                     os.path.split(parent_dir)[1] == 'pygame')
    if not is_pygame_pkg:
        sys.path.insert(0, parent_dir)
else:
    is_pygame_pkg = __name__.startswith('pygame.tests.')

if is_pygame_pkg:
    from pygame.tests import test_utils
    from pygame.tests.test_utils import test_not_implemented, unittest
else:
    from test import test_utils
    from test.test_utils import test_not_implemented, unittest
import pygame
from pygame.locals import *
from pygame.compat import xrange_

def intify(i):
    """If i is a long, cast to an int while preserving the bits"""
    if 0x10000000 & i:
        return int(~(0xFFFFFFFF ^ i))
    return i

def longify(i):
    """If i in an int, cast to a long while preserving the bits"""
    if i < 0:
        return 0xFFFFFFFF & i
    return long(i)

class SurfaceTypeTest(unittest.TestCase):
    def test_set_clip( self ):
        """ see if surface.set_clip(None) works correctly.
        """
        s = pygame.Surface((800, 600))
        r = pygame.Rect(10, 10, 10, 10)
        s.set_clip(r)
        r.move_ip(10, 0)
        s.set_clip(None)
        res = s.get_clip()
        # this was garbled before.
        self.assertEqual(res[0], 0)
        self.assertEqual(res[2], 800)

    def test_print(self):
        surf = pygame.Surface((70,70), 0, 32)
        self.assertEqual(repr(surf), '<Surface(70x70x32 SW)>')

    def test_keyword_arguments(self):
        surf = pygame.Surface((70,70), flags=SRCALPHA, depth=32)
        self.assertEqual(surf.get_flags() & SRCALPHA, SRCALPHA)
        self.assertEqual(surf.get_bitsize(), 32)
        
        # sanity check to make sure the check below is valid
        surf_16 = pygame.Surface((70,70), 0, 16)
        self.assertEqual(surf_16.get_bytesize(), 2)
        
        # try again with an argument list
        surf_16 = pygame.Surface((70,70), depth=16)
        self.assertEqual(surf_16.get_bytesize(), 2)

    def test_set_at(self):

        #24bit surfaces 
        s = pygame.Surface( (100, 100), 0, 24)
        s.fill((0,0,0))

        # set it with a tuple.
        s.set_at((0,0), (10,10,10, 255))
        r = s.get_at((0,0))
        self.assertEqual(r, (10,10,10, 255))

        # try setting a color with a single integer.
        s.fill((0,0,0,255))
        s.set_at ((10, 1), 0x0000FF)
        r = s.get_at((10,1))
        self.assertEqual(r, (0,0,255, 255))


    def test_SRCALPHA(self):
        # has the flag been passed in ok?
        surf = pygame.Surface((70,70), SRCALPHA, 32)
        self.assertEqual(surf.get_flags() & SRCALPHA, SRCALPHA)

        #24bit surfaces can not have SRCALPHA.
        self.assertRaises(ValueError, pygame.Surface, (100, 100), pygame.SRCALPHA, 24)

        # if we have a 32 bit surface, the SRCALPHA should have worked too.
        surf2 = pygame.Surface((70,70), SRCALPHA)
        if surf2.get_bitsize() == 32:
            self.assertEqual(surf2.get_flags() & SRCALPHA, SRCALPHA)

    def test_flags(self):
        def make_surf(bpp, flags, masks):
            pygame.Surface((10, 10), flags, bpp, masks)
        # With some masks SDL_CreateRGBSurface does not work properly.
        masks = (0xFF000000, 0xFF0000, 0xFF00, 0)
        self.failUnlessRaises(ValueError, make_surf, 32, 0, masks)
        # For 24 and 32 bit surfaces Pygame assumes no losses.
        masks = (0x7F0000, 0xFF00, 0xFF, 0)
        self.failUnlessRaises(ValueError, make_surf, 24, 0, masks)
        self.failUnlessRaises(ValueError, make_surf, 32, 0, masks)
        # What contiguous bits in a mask.
        masks = (0x6F0000, 0xFF00, 0xFF, 0)
        self.failUnlessRaises(ValueError, make_surf, 32, 0, masks)
        
    def test_get_buffer (self):
        surf = pygame.Surface ((70, 70), 0, 32)
        buf = surf.get_buffer ()
        # 70*70*4 bytes = 19600
        self.assertEqual (repr (buf), "<BufferProxy(19600)>")

    def test_get_bounding_rect (self):
        surf = pygame.Surface ((70, 70), SRCALPHA, 32)
        surf.fill((0,0,0,0))
        bound_rect = surf.get_bounding_rect()
        self.assertEqual(bound_rect.width, 0)
        self.assertEqual(bound_rect.height, 0)
        surf.set_at((30,30),(255,255,255,1))
        bound_rect = surf.get_bounding_rect()
        self.assertEqual(bound_rect.left, 30)
        self.assertEqual(bound_rect.top, 30)
        self.assertEqual(bound_rect.width, 1)
        self.assertEqual(bound_rect.height, 1)
        surf.set_at((29,29),(255,255,255,1))
        bound_rect = surf.get_bounding_rect()
        self.assertEqual(bound_rect.left, 29)
        self.assertEqual(bound_rect.top, 29)
        self.assertEqual(bound_rect.width, 2)
        self.assertEqual(bound_rect.height, 2)
        
        surf = pygame.Surface ((70, 70), 0, 24)
        surf.fill((0,0,0))
        bound_rect = surf.get_bounding_rect()
        self.assertEqual(bound_rect.width, surf.get_width())
        self.assertEqual(bound_rect.height, surf.get_height())

        surf.set_colorkey((0,0,0))
        bound_rect = surf.get_bounding_rect()
        self.assertEqual(bound_rect.width, 0)
        self.assertEqual(bound_rect.height, 0)
        surf.set_at((30,30),(255,255,255))
        bound_rect = surf.get_bounding_rect()
        self.assertEqual(bound_rect.left, 30)
        self.assertEqual(bound_rect.top, 30)
        self.assertEqual(bound_rect.width, 1)
        self.assertEqual(bound_rect.height, 1)
        surf.set_at((60,60),(255,255,255))
        bound_rect = surf.get_bounding_rect()
        self.assertEqual(bound_rect.left, 30)
        self.assertEqual(bound_rect.top, 30)
        self.assertEqual(bound_rect.width, 31)
        self.assertEqual(bound_rect.height, 31)

    def test_copy(self):

        # __doc__ (as of 2008-06-25) for pygame.surface.Surface.copy:

          # Surface.copy(): return Surface
          # create a new copy of a Surface
        
        color = (25, 25, 25, 25)
        s1 = pygame.Surface((32,32), pygame.SRCALPHA, 32)
        s1.fill(color)
        
        s2 = s1.copy()
        
        s1rect = s1.get_rect()
        s2rect = s2.get_rect()
        
        self.assert_(s1rect.size == s2rect.size)
        self.assert_(s2.get_at((10,10)) == color)

    def test_fill(self):

        # __doc__ (as of 2008-06-25) for pygame.surface.Surface.fill:

          # Surface.fill(color, rect=None, special_flags=0): return Rect
          # fill Surface with a solid color
        
        color = (25, 25, 25, 25)
        fill_rect = pygame.Rect(0, 0, 16, 16)
        
        s1 = pygame.Surface((32,32), pygame.SRCALPHA, 32)
        s1.fill(color, fill_rect)   
        
        for pt in test_utils.rect_area_pts(fill_rect):
            self.assert_(s1.get_at(pt) == color )
        
        for pt in test_utils.rect_outer_bounds(fill_rect):
            self.assert_(s1.get_at(pt) != color )

    def test_fill_keyword_args(self):
        color = (1, 2, 3, 255)
        area = (1, 1, 2, 2)
        s1 = pygame.Surface((4, 4), 0, 32)
        s1.fill(special_flags=pygame.BLEND_ADD, color=color, rect=area)
        self.assert_(s1.get_at((0, 0)) == (0, 0, 0, 255))
        self.assert_(s1.get_at((1, 1)) == color)
                     
    ########################################################################

    def test_get_alpha(self):

        # __doc__ (as of 2008-06-25) for pygame.surface.Surface.get_alpha:

          # Surface.get_alpha(): return int_value or None
          # get the current Surface transparency value

        s1 = pygame.Surface((32,32), pygame.SRCALPHA, 32)
        self.assert_(s1.get_alpha() == 255)
        
        for alpha in (0, 32, 127, 255):
            s1.set_alpha(alpha)
            for t in range(4): s1.set_alpha(s1.get_alpha())
            self.assert_(s1.get_alpha() == alpha)
                
    ########################################################################
    
    def test_get_bytesize(self):

        # __doc__ (as of 2008-06-25) for pygame.surface.Surface.get_bytesize:

          # Surface.get_bytesize(): return int
          # get the bytes used per Surface pixel
        
        s1 = pygame.Surface((32,32), pygame.SRCALPHA, 32)
        self.assert_(s1.get_bytesize() == 4)
        self.assert_(s1.get_bitsize() == 32)

    ########################################################################


    def test_get_flags(self):

        # __doc__ (as of 2008-06-25) for pygame.surface.Surface.get_flags:

          # Surface.get_flags(): return int
          # get the additional flags used for the Surface
        
        s1 = pygame.Surface((32,32), pygame.SRCALPHA, 32)
        self.assert_(s1.get_flags() == pygame.SRCALPHA)

    
    ########################################################################
    
    def test_get_parent(self):

        # __doc__ (as of 2008-06-25) for pygame.surface.Surface.get_parent:

          # Surface.get_parent(): return Surface
          # find the parent of a subsurface

        parent = pygame.Surface((16, 16))
        child = parent.subsurface((0,0,5,5))

        self.assert_(child.get_parent() is parent) 
        
    ########################################################################

    def test_get_rect(self):

        # __doc__ (as of 2008-06-25) for pygame.surface.Surface.get_rect:

          # Surface.get_rect(**kwargs): return Rect
          # get the rectangular area of the Surface
        
        surf = pygame.Surface((16, 16))
        
        rect = surf.get_rect()
        
        self.assert_(rect.size == (16, 16))

    ########################################################################

    def test_get_width__size_and_height(self):

        # __doc__ (as of 2008-06-25) for pygame.surface.Surface.get_width:

          # Surface.get_width(): return width
          # get the width of the Surface
        
        for w in xrange_(0, 255, 32):
            for h in xrange_(0, 127, 15):
                s = pygame.Surface((w, h))
                self.assertEquals(s.get_width(), w) 
                self.assertEquals(s.get_height(), h) 
                self.assertEquals(s.get_size(), (w, h))

    def test_set_colorkey(self):

        # __doc__ (as of 2008-06-25) for pygame.surface.Surface.set_colorkey:

          # Surface.set_colorkey(Color, flags=0): return None
          # Surface.set_colorkey(None): return None
          # Set the transparent colorkey
        
        s = pygame.Surface((16,16), pygame.SRCALPHA, 32)
        
        colorkeys = ((20,189,20, 255),(128,50,50,255), (23, 21, 255,255))

        for colorkey in colorkeys:
            s.set_colorkey(colorkey)
            for t in range(4): s.set_colorkey(s.get_colorkey())
            self.assertEquals(s.get_colorkey(), colorkey) 



    def test_set_masks(self):
        s = pygame.Surface((32,32))
        r,g,b,a = s.get_masks()
        s.set_masks((b,g,r,a))
        r2,g2,b2,a2 = s.get_masks()
        self.assertEqual((r,g,b,a), (b2,g2,r2,a2))


    def test_set_shifts(self):
        s = pygame.Surface((32,32))
        r,g,b,a = s.get_shifts()
        s.set_shifts((b,g,r,a))
        r2,g2,b2,a2 = s.get_shifts()
        self.assertEqual((r,g,b,a), (b2,g2,r2,a2))
    
    def test_blit_keyword_args(self):
        color = (1, 2, 3, 255)
        s1 = pygame.Surface((4, 4), 0, 32)
        s2 = pygame.Surface((2, 2), 0, 32)
        s2.fill((1, 2, 3))
        s1.blit(special_flags=BLEND_ADD, source=s2,
                dest=(1, 1), area=s2.get_rect())
        self.assertEqual(s1.get_at((0, 0)), (0, 0, 0, 255))
        self.assertEqual(s1.get_at((1, 1)), color)

    def todo_test_blit(self):
        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.blit:

          # Surface.blit(source, dest, area=None, special_flags = 0): return Rect
          # draw one image onto another
          #
          # Draws a source Surface onto this Surface. The draw can be positioned
          # with the dest argument. Dest can either be pair of coordinates
          # representing the upper left corner of the source. A Rect can also be
          # passed as the destination and the topleft corner of the rectangle
          # will be used as the position for the blit. The size of the
          # destination rectangle does not effect the blit.
          #
          # An optional area rectangle can be passed as well. This represents a
          # smaller portion of the source Surface to draw.
          #
          # An optional special flags is for passing in new in 1.8.0: BLEND_ADD,
          # BLEND_SUB, BLEND_MULT, BLEND_MIN, BLEND_MAX new in 1.8.1:
          # BLEND_RGBA_ADD, BLEND_RGBA_SUB, BLEND_RGBA_MULT, BLEND_RGBA_MIN,
          # BLEND_RGBA_MAX BLEND_RGB_ADD, BLEND_RGB_SUB, BLEND_RGB_MULT,
          # BLEND_RGB_MIN, BLEND_RGB_MAX With other special blitting flags
          # perhaps added in the future.
          #
          # The return rectangle is the area of the affected pixels, excluding
          # any pixels outside the destination Surface, or outside the clipping
          # area.
          #
          # Pixel alphas will be ignored when blitting to an 8 bit Surface. 
          # special_flags new in pygame 1.8. 

        self.fail()

    def test_blit__SRCALPHA_opaque_source(self):
        src = pygame.Surface( (256,256), SRCALPHA ,32)
        dst = src.copy()

        for i, j in test_utils.rect_area_pts(src.get_rect()):
            dst.set_at( (i,j), (i,0,0,j) )
            src.set_at( (i,j), (0,i,0,255) )

        dst.blit(src, (0,0))

        for pt in test_utils.rect_area_pts(src.get_rect()):
            self.assertEquals ( dst.get_at(pt)[1], src.get_at(pt)[1] )

    def todo_test_blit__blit_to_self(self): #TODO
        src = pygame.Surface( (256,256), SRCALPHA, 32)
        rect = src.get_rect()

        for pt, color in test_utils.gradient(rect.width, rect.height):
            src.set_at(pt, color)
        
        src.blit(src, (0, 0))
        
    def todo_test_blit__SRCALPHA_to_SRCALPHA_non_zero(self): #TODO
        # " There is no unit test for blitting a SRCALPHA source with non-zero
        #   alpha to a SRCALPHA destination with non-zero alpha " LL

        w,h = size = 32,32

        s = pygame.Surface(size, pygame.SRCALPHA, 32)
        s2 = s.copy()

        s.fill((32,32,32,111))
        s2.fill((32,32,32,31))

        s.blit(s2, (0,0))

        # TODO:
        # what is the correct behaviour ?? should it blend? what algorithm?

        self.assertEquals(s.get_at((0,0)), (32,32,32,31))

    def todo_test_convert(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.convert:

          # Surface.convert(Surface): return Surface
          # Surface.convert(depth, flags=0): return Surface
          # Surface.convert(masks, flags=0): return Surface
          # Surface.convert(): return Surface
          # change the pixel format of an image
          # 
          # Creates a new copy of the Surface with the pixel format changed. The
          # new pixel format can be determined from another existing Surface.
          # Otherwise depth, flags, and masks arguments can be used, similar to
          # the pygame.Surface() call.
          # 
          # If no arguments are passed the new Surface will have the same pixel
          # format as the display Surface. This is always the fastest format for
          # blitting. It is a good idea to convert all Surfaces before they are
          # blitted many times.
          # 
          # The converted Surface will have no pixel alphas. They will be
          # stripped if the original had them. See Surface.convert_alpha() for
          # preserving or creating per-pixel alphas.
          # 

        self.fail() 

    def todo_test_convert_alpha(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.convert_alpha:

          # Surface.convert_alpha(Surface): return Surface
          # Surface.convert_alpha(): return Surface
          # change the pixel format of an image including per pixel alphas
          # 
          # Creates a new copy of the surface with the desired pixel format. The
          # new surface will be in a format suited for quick blitting to the
          # given format with per pixel alpha. If no surface is given, the new
          # surface will be optimized for blitting to the current display.
          # 
          # Unlike the Surface.convert() method, the pixel format for the new
          # image will not be exactly the same as the requested source, but it
          # will be optimized for fast alpha blitting to the destination.
          # 

        self.fail() 

    def todo_test_get_abs_offset(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_abs_offset:

          # Surface.get_abs_offset(): return (x, y)
          # find the absolute position of a child subsurface inside its top level parent
          # 
          # Get the offset position of a child subsurface inside of its top
          # level parent Surface. If the Surface is not a subsurface this will
          # return (0, 0).
          # 

        self.fail() 

    def todo_test_get_abs_parent(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_abs_parent:

          # Surface.get_abs_parent(): return Surface
          # find the top level parent of a subsurface
          # 
          # Returns the parent Surface of a subsurface. If this is not a
          # subsurface then this surface will be returned.
          # 

        self.fail() 

    def todo_test_get_at(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_at:

          # Surface.get_at((x, y)): return Color
          # get the color value at a single pixel
          # 
          # Return the RGBA color value at the given pixel. If the Surface has
          # no per pixel alpha, then the alpha value will always be 255
          # (opaque). If the pixel position is outside the area of the Surface
          # an IndexError exception will be raised.
          # 
          # Getting and setting pixels one at a time is generally too slow to be
          # used in a game or realtime situation.
          # 
          # This function will temporarily lock and unlock the Surface as needed. 

        self.fail() 

    def todo_test_get_bitsize(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_bitsize:

          # Surface.get_bitsize(): return int
          # get the bit depth of the Surface pixel format
          # 
          # Returns the number of bits used to represent each pixel. This value
          # may not exactly fill the number of bytes used per pixel. For example
          # a 15 bit Surface still requires a full 2 bytes.
          # 

        self.fail() 

    def todo_test_get_clip(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_clip:

          # Surface.get_clip(): return Rect
          # get the current clipping area of the Surface
          # 
          # Return a rectangle of the current clipping area. The Surface will
          # always return a valid rectangle that will never be outside the
          # bounds of the image. If the Surface has had None set for the
          # clipping area, the Surface will return a rectangle with the full
          # area of the Surface.
          # 

        self.fail() 

    def todo_test_get_colorkey(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_colorkey:

          # Surface.get_colorkey(): return RGB or None
          # Get the current transparent colorkey
          # 
          # Return the current colorkey value for the Surface. If the colorkey
          # is not set then None is returned.
          # 

        self.fail() 

    def todo_test_get_height(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_height:

          # Surface.get_height(): return height
          # get the height of the Surface
          # 
          # Return the height of the Surface in pixels. 

        self.fail() 

    def todo_test_get_locked(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_locked:

          # Surface.get_locked(): return bool
          # test if the Surface is current locked
          # 
          # Returns True when the Surface is locked. It doesn't matter how many
          # times the Surface is locked.
          # 

        self.fail() 

    def todo_test_get_locks(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_locks:

          # Surface.get_locks(): return tuple
          # Gets the locks for the Surface
          # 
          # Returns the currently existing locks for the Surface. 

        self.fail() 

    def todo_test_get_losses(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_losses:

          # Surface.get_losses(): return (R, G, B, A)
          # the significant bits used to convert between a color and a mapped integer
          # 
          # Return the least significant number of bits stripped from each color
          # in a mapped integer.
          # 
          # This value is not needed for normal Pygame usage. 

        self.fail() 

    def todo_test_get_masks(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_masks:

          # Surface.get_masks(): return (R, G, B, A)
          # the bitmasks needed to convert between a color and a mapped integer
          # 
          # Returns the bitmasks used to isolate each color in a mapped integer. 
          # This value is not needed for normal Pygame usage. 

        self.fail() 

    def todo_test_get_offset(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_offset:

          # Surface.get_offset(): return (x, y)
          # find the position of a child subsurface inside a parent
          # 
          # Get the offset position of a child subsurface inside of a parent. If
          # the Surface is not a subsurface this will return (0, 0).
          # 

        self.fail() 

    def todo_test_get_palette(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_palette:

          # Surface.get_palette(): return [RGB, RGB, RGB, ...]
          # get the color index palette for an 8bit Surface
          # 
          # Return a list of up to 256 color elements that represent the indexed
          # colors used in an 8bit Surface. The returned list is a copy of the
          # palette, and changes will have no effect on the Surface.
          # 

        self.fail() 

    def todo_test_get_palette_at(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_palette_at:

          # Surface.get_palette_at(index): return RGB
          # get the color for a single entry in a palette
          # 
          # Returns the red, green, and blue color values for a single index in
          # a Surface palette. The index should be a value from 0 to 255.
          # 

        self.fail() 

    def todo_test_get_pitch(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_pitch:

          # Surface.get_pitch(): return int
          # get the number of bytes used per Surface row
          # 
          # Return the number of bytes separating each row in the Surface.
          # Surfaces in video memory are not always linearly packed. Subsurfaces
          # will also have a larger pitch than their real width.
          # 
          # This value is not needed for normal Pygame usage. 

        self.fail() 

    def todo_test_get_shifts(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_shifts:

          # Surface.get_shifts(): return (R, G, B, A)
          # the bit shifts needed to convert between a color and a mapped integer
          # 
          # Returns the pixel shifts need to convert between each color and a
          # mapped integer.
          # 
          # This value is not needed for normal Pygame usage. 

        self.fail() 

    def todo_test_get_size(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.get_size:

          # Surface.get_size(): return (width, height)
          # get the dimensions of the Surface
          # 
          # Return the width and height of the Surface in pixels. 

        self.fail() 

    def todo_test_lock(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.lock:

          # Surface.lock(): return None
          # lock the Surface memory for pixel access
          # 
          # Lock the pixel data of a Surface for access. On accelerated
          # Surfaces, the pixel data may be stored in volatile video memory or
          # nonlinear compressed forms. When a Surface is locked the pixel
          # memory becomes available to access by regular software. Code that
          # reads or writes pixel values will need the Surface to be locked.
          # 
          # Surfaces should not remain locked for more than necessary. A locked
          # Surface can often not be displayed or managed by Pygame.
          # 
          # Not all Surfaces require locking. The Surface.mustlock() method can
          # determine if it is actually required. There is no performance
          # penalty for locking and unlocking a Surface that does not need it.
          # 
          # All pygame functions will automatically lock and unlock the Surface
          # data as needed. If a section of code is going to make calls that
          # will repeatedly lock and unlock the Surface many times, it can be
          # helpful to wrap the block inside a lock and unlock pair.
          # 
          # It is safe to nest locking and unlocking calls. The surface will
          # only be unlocked after the final lock is released.
          # 

        self.fail() 

    def test_map_rgb(self):

        color = Color(0, 128, 255, 64)
        surf = pygame.Surface((5, 5), SRCALPHA, 32)
        c = surf.map_rgb(color)
        self.failUnlessEqual(surf.unmap_rgb(c), color)

        self.failUnlessEqual(surf.get_at((0, 0)), (0, 0, 0, 0))
        surf.fill(c)
        self.failUnlessEqual(surf.get_at((0, 0)), color)

        surf.fill((0, 0, 0, 0))
        self.failUnlessEqual(surf.get_at((0, 0)), (0, 0, 0, 0))
        surf.set_at((0, 0), c)
        self.failUnlessEqual(surf.get_at((0, 0)), color)

    def todo_test_mustlock(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.mustlock:

          # Surface.mustlock(): return bool
          # test if the Surface requires locking
          # 
          # Returns True if the Surface is required to be locked to access pixel
          # data. Usually pure software Surfaces do not require locking. This
          # method is rarely needed, since it is safe and quickest to just lock
          # all Surfaces as needed.
          # 
          # All pygame functions will automatically lock and unlock the Surface
          # data as needed. If a section of code is going to make calls that
          # will repeatedly lock and unlock the Surface many times, it can be
          # helpful to wrap the block inside a lock and unlock pair.
          # 

        self.fail() 

    def todo_test_set_alpha(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.set_alpha:

          # Surface.set_alpha(value, flags=0): return None
          # Surface.set_alpha(None): return None
          # set the alpha value for the full Surface image
          # 
          # Set the current alpha value fo r the Surface. When blitting this
          # Surface onto a destination, the pixels will be drawn slightly
          # transparent. The alpha value is an integer from 0 to 255, 0 is fully
          # transparent and 255 is fully opaque. If None is passed for the alpha
          # value, then the Surface alpha will be disabled.
          # 
          # This value is different than the per pixel Surface alpha. If the
          # Surface format contains per pixel alphas, then this alpha value will
          # be ignored. If the Surface contains per pixel alphas, setting the
          # alpha value to None will disable the per pixel transparency.
          # 
          # The optional flags argument can be set to pygame.RLEACCEL to provide
          # better performance on non accelerated displays. An RLEACCEL Surface
          # will be slower to modify, but quicker to blit as a source.
          # 

        s = pygame.Surface((1,1), SRCALHPA, 32)
        s.fill((1, 2, 3, 4))
        s.set_alpha(None)
        self.failUnlessEqual(s.get_at((0, 0)), (1, 2, 3, 255))
        self.fail() 

    def todo_test_set_palette(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.set_palette:

          # Surface.set_palette([RGB, RGB, RGB, ...]): return None
          # set the color palette for an 8bit Surface
          # 
          # Set the full palette for an 8bit Surface. This will replace the
          # colors in the existing palette. A partial palette can be passed and
          # only the first colors in the original palette will be changed.
          # 
          # This function has no effect on a Surface with more than 8bits per pixel. 

        self.fail() 

    def todo_test_set_palette_at(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.set_palette_at:

          # Surface.set_at(index, RGB): return None
          # set the color for a single index in an 8bit Surface palette
          # 
          # Set the palette value for a single entry in a Surface palette. The
          # index should be a value from 0 to 255.
          # 
          # This function has no effect on a Surface with more than 8bits per pixel. 

        self.fail() 

    def test_subsurface(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.subsurface:

          # Surface.subsurface(Rect): return Surface
          # create a new surface that references its parent
          # 
          # Returns a new Surface that shares its pixels with its new parent.
          # The new Surface is considered a child of the original. Modifications
          # to either Surface pixels will effect each other. Surface information
          # like clipping area and color keys are unique to each Surface.
          # 
          # The new Surface will inherit the palette, color key, and alpha
          # settings from its parent.
          # 
          # It is possible to have any number of subsurfaces and subsubsurfaces
          # on the parent. It is also possible to subsurface the display Surface
          # if the display mode is not hardware accelerated.
          # 
          # See the Surface.get_offset(), Surface.get_parent() to learn more
          # about the state of a subsurface.
          # 

        surf = pygame.Surface((16, 16))
        s = surf.subsurface(0,0,1,1)
        s = surf.subsurface((0,0,1,1))



        #s = surf.subsurface((0,0,1,1), 1)
        # This form is not acceptable.
        #s = surf.subsurface(0,0,10,10, 1)

        self.assertRaises(ValueError, surf.subsurface, (0,0,1,1,666))


        self.assertEquals(s.get_shifts(), surf.get_shifts())
        self.assertEquals(s.get_masks(), surf.get_masks())
        self.assertEquals(s.get_losses(), surf.get_losses())





    def todo_test_unlock(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.unlock:

          # Surface.unlock(): return None
          # unlock the Surface memory from pixel access
          # 
          # Unlock the Surface pixel data after it has been locked. The unlocked
          # Surface can once again be drawn and managed by Pygame. See the
          # Surface.lock() documentation for more details.
          # 
          # All pygame functions will automatically lock and unlock the Surface
          # data as needed. If a section of code is going to make calls that
          # will repeatedly lock and unlock the Surface many times, it can be
          # helpful to wrap the block inside a lock and unlock pair.
          # 
          # It is safe to nest locking and unlocking calls. The surface will
          # only be unlocked after the final lock is released.
          # 

        self.fail() 

    def todo_test_unmap_rgb(self):

        # __doc__ (as of 2008-08-02) for pygame.surface.Surface.unmap_rgb:

          # Surface.map_rgb(mapped_int): return Color
          # convert a mapped integer color value into a Color
          # 
          # Convert an mapped integer color into the RGB color components for
          # this Surface. Mapped color values are not often used inside Pygame,
          # but can be passed to most functions that require a Surface and a
          # color.
          # 
          # See the Surface object documentation for more information about
          # colors and pixel formats.
          # 

        self.fail()

    def test_scroll(self):
        scrolls = [(8, 2, 3),
                   (16, 2, 3),
                   (24, 2, 3),
                   (32, 2, 3),
                   (32, -1, -3),
                   (32, 0, 0),
                   (32, 11, 0),
                   (32, 0, 11),
                   (32, -11, 0),
                   (32, 0, -11),
                   (32, -11, 2),
                   (32, 2, -11)]
        for bitsize, dx, dy in scrolls:
            surf = pygame.Surface((10, 10), 0, bitsize)
            surf.fill((255, 0, 0))
            surf.fill((0, 255, 0), (2, 2, 2, 2,))
            comp = surf.copy()
            comp.blit(surf, (dx, dy))
            surf.scroll(dx, dy)
            w, h = surf.get_size()
            for x in range(w):
                for y in range(h):
                    self.failUnlessEqual(surf.get_at((x, y)),
                                         comp.get_at((x, y)),
                                         "%s != %s, bpp:, %i, x: %i, y: %i" %
                                         (surf.get_at((x, y)),
                                          comp.get_at((x, y)),
                                          bitsize, dx, dy))
        # Confirm clip rect containment
        surf = pygame.Surface((20, 13), 0, 32)
        surf.fill((255, 0, 0))
        surf.fill((0, 255, 0), (7, 1, 6, 6))
        comp = surf.copy()
        clip = Rect(3, 1, 8, 14)
        surf.set_clip(clip)
        comp.set_clip(clip)
        comp.blit(surf, (clip.x + 2, clip.y + 3), surf.get_clip())
        surf.scroll(2, 3)
        w, h = surf.get_size()
        for x in range(w):
            for y in range(h):
                self.failUnlessEqual(surf.get_at((x, y)),
                                     comp.get_at((x, y)))
        # Confirm keyword arguments and per-pixel alpha
        spot_color = (0, 255, 0, 128)
        surf = pygame.Surface((4, 4), pygame.SRCALPHA, 32)
        surf.fill((255, 0, 0, 255))
        surf.set_at((1, 1), spot_color)
        surf.scroll(dx=1)
        self.failUnlessEqual(surf.get_at((2, 1)), spot_color)
        surf.scroll(dy=1)
        self.failUnlessEqual(surf.get_at((2, 2)), spot_color)
        surf.scroll(dy=1, dx=1)
        self.failUnlessEqual(surf.get_at((3, 3)), spot_color)
        surf.scroll(dx=-3, dy=-3)
        self.failUnlessEqual(surf.get_at((0, 0)), spot_color)

class SurfaceBlendTest (unittest.TestCase):

    test_palette = [(0, 0, 0, 255),
                    (10, 30, 60, 0),
                    (25, 75, 100, 128),
                    (200, 150, 100, 200),
                    (0, 100, 200, 255)]
    surf_size = (10, 12)
    test_points = [((0, 0), 1), ((4, 5), 1), ((9, 0), 2),
                   ((5, 5), 2), ((0, 11), 3), ((4, 6), 3),
                   ((9, 11), 4), ((5, 6), 4)]

    def _make_surface(self, bitsize, srcalpha=False, palette=None):
        if palette is None:
            palette = self.test_palette
        flags = 0
        if srcalpha:
            flags |= SRCALPHA
        surf = pygame.Surface(self.surf_size, flags, bitsize)
        if bitsize == 8:
            surf.set_palette([c[:3] for c in palette])
        return surf

    def _fill_surface(self, surf, palette=None):
        if palette is None:
            palette = self.test_palette
        surf.fill(palette[1], (0, 0, 5, 6))
        surf.fill(palette[2], (5, 0, 5, 6))
        surf.fill(palette[3], (0, 6, 5, 6))
        surf.fill(palette[4], (5, 6, 5, 6))

    def _make_src_surface(self, bitsize, srcalpha=False, palette=None):
        surf = self._make_surface(bitsize, srcalpha, palette)
        self._fill_surface(surf, palette)
        return surf

    def _assert_surface(self, surf, palette=None, msg=""):
        if palette is None:
            palette = self.test_palette
        if surf.get_bitsize() == 16:
            palette = [surf.unmap_rgb(surf.map_rgb(c)) for c in palette]
        for posn, i in self.test_points:
            self.failUnlessEqual(surf.get_at(posn), palette[i],
                                 "%s != %s: flags: %i, bpp: %i, posn: %s%s" %
                                 (surf.get_at(posn),
                                  palette[i], surf.get_flags(),
                                  surf.get_bitsize(), posn, msg))

    def setUp(self):
        # Needed for 8 bits-per-pixel color palette surface tests.
        pygame.init()

    def tearDown(self):
        pygame.quit()

    def test_blit_blend(self):
        sources = [self._make_src_surface(8),
                   self._make_src_surface(16),
                   self._make_src_surface(16, srcalpha=True),
                   self._make_src_surface(24),
                   self._make_src_surface(32),
                   self._make_src_surface(32, srcalpha=True)]
        destinations = [self._make_surface(8),
                        self._make_surface(16),
                        self._make_surface(16, srcalpha=True),
                        self._make_surface(24),
                        self._make_surface(32),
                        self._make_surface(32, srcalpha=True)]
        blend = [('BLEND_ADD', (0, 25, 100, 255),
                  lambda a, b: min(a + b, 255)),
                 ('BLEND_SUB', (100, 25, 0, 100),
                  lambda a, b: max(a - b, 0)),
                 ('BLEND_MULT', (100, 200, 0, 0),
                  lambda a, b: (a * b) // 256),
                 ('BLEND_MIN', (255, 0, 0, 255), min),
                 ('BLEND_MAX', (0, 255, 0, 255), max)]

        for src in sources:
            src_palette = [src.unmap_rgb(src.map_rgb(c))
                           for c in self.test_palette]
            for dst in destinations:
                for blend_name, dst_color, op in blend:
                    dc = dst.unmap_rgb(dst.map_rgb(dst_color))
                    p = []
                    for sc in src_palette:
                        c = [op(dc[i], sc[i]) for i in range(3)]
                        if dst.get_masks()[3]:
                            c.append(dc[3])
                        else:
                            c.append(255)
                        c = dst.unmap_rgb(dst.map_rgb(c))
                        p.append(c)
                    dst.fill(dst_color)
                    dst.blit(src,
                              (0, 0),
                              special_flags=getattr(pygame, blend_name))
                    self._assert_surface(dst, p,
                                         (", op: %s, src bpp: %i"
                                          ", src flags: %i" %
                                          (blend_name,
                                           src.get_bitsize(),
                                           src.get_flags())))

        src = self._make_src_surface(32)
        masks = src.get_masks()
        dst = pygame.Surface(src.get_size(), 0, 32,
                             [masks[1], masks[2], masks[0], masks[3]])
        for blend_name, dst_color, op in blend:
            p = []
            for src_color in self.test_palette:
                c = [op(dst_color[i], src_color[i]) for i in range(3)]
                c.append(255)
                p.append(tuple(c))
            dst.fill(dst_color)
            dst.blit(src,
                     (0, 0),
                     special_flags=getattr(pygame, blend_name))
            self._assert_surface(dst, p, ", %s" % blend_name)

        # Blend blits are special cased for 32 to 32 bit surfaces.
        #
        # Confirm that it works when the rgb bytes are not the
        # least significant bytes.
        pat = self._make_src_surface(32)
        masks = pat.get_masks()
        if min(masks) == intify(0xFF000000):
            masks = [longify(m) >> 8 for m in masks]
        else:
            masks = [intify(m << 8) for m in masks]
        src = pygame.Surface(pat.get_size(), 0, 32, masks)
        self._fill_surface(src)
        dst = pygame.Surface(src.get_size(), 0, 32, masks)
        for blend_name, dst_color, op in blend:
            p = []
            for src_color in self.test_palette:
                c = [op(dst_color[i], src_color[i]) for i in range(3)]
                c.append(255)
                p.append(tuple(c))
            dst.fill(dst_color)
            dst.blit(src,
                     (0, 0),
                     special_flags=getattr(pygame, blend_name))
            self._assert_surface(dst, p, ", %s" % blend_name)

    def test_blit_blend_rgba(self):
        sources = [self._make_src_surface(8),
                   self._make_src_surface(16),
                   self._make_src_surface(16, srcalpha=True),
                   self._make_src_surface(24),
                   self._make_src_surface(32),
                   self._make_src_surface(32, srcalpha=True)]
        destinations = [self._make_surface(8),
                        self._make_surface(16),
                        self._make_surface(16, srcalpha=True),
                        self._make_surface(24),
                        self._make_surface(32),
                        self._make_surface(32, srcalpha=True)]
        blend = [('BLEND_RGBA_ADD', (0, 25, 100, 255),
                  lambda a, b: min(a + b, 255)),
                 ('BLEND_RGBA_SUB', (0, 25, 100, 255),
                  lambda a, b: max(a - b, 0)),
                 ('BLEND_RGBA_MULT', (0, 7, 100, 255),
                  lambda a, b: (a * b) // 256),
                 ('BLEND_RGBA_MIN', (0, 255, 0, 255), min),
                 ('BLEND_RGBA_MAX', (0, 255, 0, 255), max)]

        for src in sources:
            src_palette = [src.unmap_rgb(src.map_rgb(c))
                           for c in self.test_palette]
            for dst in destinations:
                for blend_name, dst_color, op in blend:
                    dc = dst.unmap_rgb(dst.map_rgb(dst_color))
                    p = []
                    for sc in src_palette:
                        c = [op(dc[i], sc[i]) for i in range(4)]
                        if not dst.get_masks()[3]:
                            c[3] = 255
                        c = dst.unmap_rgb(dst.map_rgb(c))
                        p.append(c)
                    dst.fill(dst_color)
                    dst.blit(src,
                              (0, 0),
                              special_flags=getattr(pygame, blend_name))
                    self._assert_surface(dst, p,
                                         (", op: %s, src bpp: %i"
                                          ", src flags: %i" %
                                          (blend_name,
                                           src.get_bitsize(),
                                           src.get_flags())))

        # Blend blits are special cased for 32 to 32 bit surfaces
        # with per-pixel alpha.
        #
        # Confirm the general case is used instead when the formats differ.
        src = self._make_src_surface(32, srcalpha=True)
        masks = src.get_masks()
        dst = pygame.Surface(src.get_size(), SRCALPHA, 32,
                             (masks[1], masks[2], masks[3], masks[0]))
        for blend_name, dst_color, op in blend:
            p = [tuple([op(dst_color[i], src_color[i]) for i in range(4)])
                 for src_color in self.test_palette]
            dst.fill(dst_color)
            dst.blit(src,
                     (0, 0),
                     special_flags=getattr(pygame, blend_name))
            self._assert_surface(dst, p, ", %s" % blend_name)

        # Confirm this special case handles subsurfaces.
        src = pygame.Surface((8, 10), SRCALPHA, 32)
        dst = pygame.Surface((8, 10), SRCALPHA, 32)
        tst = pygame.Surface((8, 10), SRCALPHA, 32)
        src.fill((1, 2, 3, 4))
        dst.fill((40, 30, 20, 10))
        subsrc = src.subsurface((2, 3, 4, 4))
        try:
            subdst = dst.subsurface((2, 3, 4, 4))
            try:
                subdst.blit(subsrc, (0, 0), special_flags=BLEND_RGBA_ADD)
            finally:
                del subdst
        finally:
            del subsrc
        tst.fill((40, 30, 20, 10))
        tst.fill((41, 32, 23, 14), (2, 3, 4, 4))
        for x in range(8):
            for y in range(10):
                self.failUnlessEqual(dst.get_at((x, y)), tst.get_at((x, y)),
                                     "%s != %s at (%i, %i)" %
                                     (dst.get_at((x, y)), tst.get_at((x, y)),
                                      x, y))

    def test_GET_PIXELVALS(self):
        # surface.h GET_PIXELVALS bug regarding whether of not
        # a surface has per-pixel alpha. Looking at the Amask
        # is not enough. The surface's SRCALPHA flag must also
        # be considered. Fix rev. 1923.
        src = self._make_surface(32, srcalpha=True)
        src.fill((0, 0, 0, 128))
        src.set_alpha(None)  # Clear SRCALPHA flag.
        dst = self._make_surface(32, srcalpha=True)
        dst.blit(src, (0, 0), special_flags=BLEND_RGBA_ADD)
        self.failUnlessEqual(dst.get_at((0, 0)), (0, 0, 0, 255))
        
    def test_fill_blend(self):
        destinations = [self._make_surface(8),
                        self._make_surface(16),
                        self._make_surface(16, srcalpha=True),
                        self._make_surface(24),
                        self._make_surface(32),
                        self._make_surface(32, srcalpha=True)]
        blend = [('BLEND_ADD', (0, 25, 100, 255),
                  lambda a, b: min(a + b, 255)),
                 ('BLEND_SUB', (0, 25, 100, 255),
                  lambda a, b: max(a - b, 0)),
                 ('BLEND_MULT', (0, 7, 100, 255),
                  lambda a, b: (a * b) // 256),
                 ('BLEND_MIN', (0, 255, 0, 255), min),
                 ('BLEND_MAX', (0, 255, 0, 255), max)]

        for dst in destinations:
            dst_palette = [dst.unmap_rgb(dst.map_rgb(c))
                           for c in self.test_palette]
            for blend_name, fill_color, op in blend:
                fc = dst.unmap_rgb(dst.map_rgb(fill_color))
                self._fill_surface(dst)
                p = []
                for dc in dst_palette:
                    c = [op(dc[i], fc[i]) for i in range(3)]
                    if dst.get_masks()[3]:
                        c.append(dc[3])
                    else:
                        c.append(255)
                    c = dst.unmap_rgb(dst.map_rgb(c))
                    p.append(c)
                dst.fill(fill_color, special_flags=getattr(pygame, blend_name))
                self._assert_surface(dst, p, ", %s" % blend_name)

    def test_fill_blend_rgba(self):
        destinations = [self._make_surface(8),
                        self._make_surface(16),
                        self._make_surface(16, srcalpha=True),
                        self._make_surface(24),
                        self._make_surface(32),
                        self._make_surface(32, srcalpha=True)]
        blend = [('BLEND_RGBA_ADD', (0, 25, 100, 255),
                  lambda a, b: min(a + b, 255)),
                 ('BLEND_RGBA_SUB', (0, 25, 100, 255),
                  lambda a, b: max(a - b, 0)),
                 ('BLEND_RGBA_MULT', (0, 7, 100, 255),
                  lambda a, b: (a * b) // 256),
                 ('BLEND_RGBA_MIN', (0, 255, 0, 255), min),
                 ('BLEND_RGBA_MAX', (0, 255, 0, 255), max)]

        for dst in destinations:
            dst_palette = [dst.unmap_rgb(dst.map_rgb(c))
                           for c in self.test_palette]
            for blend_name, fill_color, op in blend:
                fc = dst.unmap_rgb(dst.map_rgb(fill_color))
                self._fill_surface(dst)
                p = []
                for dc in dst_palette:
                    c = [op(dc[i], fc[i]) for i in range(4)]
                    if not dst.get_masks()[3]:
                        c[3] = 255
                    c = dst.unmap_rgb(dst.map_rgb(c))
                    p.append(c)
                dst.fill(fill_color, special_flags=getattr(pygame, blend_name))
                self._assert_surface(dst, p, ", %s" % blend_name)

class SurfaceSelfBlitTest(unittest.TestCase):
    """Blit to self tests.

    This test case is in response to MotherHamster Bugzilla Bug 19.
    """

    test_palette = [(0, 0, 0, 255),
                    (255, 0, 0, 0),
                    (0, 255, 0, 255)]
    surf_size = (9, 6)
    
    def _fill_surface(self, surf, palette=None):
        if palette is None:
            palette = self.test_palette
        surf.fill(palette[1])
        surf.fill(palette[2], (1, 2, 1, 2))

    def _make_surface(self, bitsize, srcalpha=False, palette=None):
        if palette is None:
            palette = self.test_palette
        flags = 0
        if srcalpha:
            flags |= SRCALPHA
        surf = pygame.Surface(self.surf_size, flags, bitsize)
        if bitsize == 8:
            surf.set_palette([c[:3] for c in palette])
        self._fill_surface(surf, palette)
        return surf

    def _assert_same(self, a, b):
        w, h = a.get_size()
        for x in range(w):
            for y in range(h):
                self.failUnlessEqual(a.get_at((x, y)), b.get_at((x, y)),
                                     ("%s != %s, bpp: %i" %
                                      (a.get_at((x, y)), b.get_at((x, y)),
                                       a.get_bitsize())))

    def setUp(self):
        # Needed for 8 bits-per-pixel color palette surface tests.
        pygame.init()

    def tearDown(self):
        pygame.quit()

    def test_overlap_check(self):
        # Ensure overlapping blits are properly detected. There are two
        # places where this is done, within SoftBlitPyGame() in alphablit.c
        # and PySurface_Blit() in surface.c. SoftBlitPyGame should catch the
        # per-pixel alpha surface, PySurface_Blit the colorkey and blanket
        # alpha surface. per-pixel alpha and blanket alpha self blits are
        # not properly handled by SDL 1.2.13, so Pygame does them.
        bgc = (0, 0, 0, 255)
        rectc_left = (128, 64, 32, 255)
        rectc_right = (255, 255, 255, 255)
        colors = [(255, 255, 255, 255), (128, 64, 32, 255)]
        overlaps = [(0, 0, 1, 0, (50, 0)),
                    (0, 0, 49, 1, (98, 2)),
                    (0, 0, 49, 49, (98, 98)),
                    (49, 0, 0, 1, (0, 2)),
                    (49, 0, 0, 49, (0, 98))]
        surfs = [pygame.Surface((100, 100), SRCALPHA, 32)]
        surf = pygame.Surface((100, 100), 0, 32)
        surf.set_alpha(255)
        surfs.append(surf)
        surf = pygame.Surface((100, 100), 0, 32)
        surf.set_colorkey((0, 1, 0))
        surfs.append(surf)
        for surf in surfs:
            for s_x, s_y, d_x, d_y, test_posn in overlaps:
                surf.fill(bgc)
                surf.fill(rectc_right, (25, 0, 25, 50))
                surf.fill(rectc_left, (0, 0, 25, 50))
                surf.blit(surf, (d_x, d_y), (s_x, s_y, 50, 50))
                self.failUnlessEqual(surf.get_at(test_posn), rectc_right)
         
    def test_colorkey(self):
        # Check a workaround for an SDL 1.2.13 surface self-blit problem
        # (MotherHamster Bugzilla bug 19).
        pygame.display.set_mode((100, 50))  # Needed for 8bit surface
        bitsizes = [8, 16, 24, 32]
        for bitsize in bitsizes:
            surf = self._make_surface(bitsize)
            surf.set_colorkey(self.test_palette[1])
            surf.blit(surf, (3, 0))
            p = []
            for c in self.test_palette:
                c = surf.unmap_rgb(surf.map_rgb(c))
                p.append(c)
            p[1] = (p[1][0], p[1][1], p[1][2], 0)
            tmp = self._make_surface(32, srcalpha=True, palette=p)
            tmp.blit(tmp, (3, 0))
            tmp.set_alpha(None)
            comp = self._make_surface(bitsize)
            comp.blit(tmp, (0, 0))
            self._assert_same(surf, comp)

    def test_blanket_alpha(self):
        # Check a workaround for an SDL 1.2.13 surface self-blit problem
        # (MotherHamster Bugzilla bug 19).
        pygame.display.set_mode((100, 50))  # Needed for 8bit surface
        bitsizes = [8, 16, 24, 32]
        for bitsize in bitsizes:
            surf = self._make_surface(bitsize)
            surf.set_alpha(128)
            surf.blit(surf, (3, 0))
            p = []
            for c in self.test_palette:
                c = surf.unmap_rgb(surf.map_rgb(c))
                p.append((c[0], c[1], c[2], 128))
            tmp = self._make_surface(32, srcalpha=True, palette=p)
            tmp.blit(tmp, (3, 0))
            tmp.set_alpha(None)
            comp = self._make_surface(bitsize)
            comp.blit(tmp, (0, 0))
            self._assert_same(surf, comp)

    def test_pixel_alpha(self):
        bitsizes = [16, 32]
        for bitsize in bitsizes:
            surf = self._make_surface(bitsize, srcalpha=True)
            comp = self._make_surface(bitsize, srcalpha=True)
            comp.blit(surf, (3, 0))
            surf.blit(surf, (3, 0))
            self._assert_same(surf, comp)

    def test_blend(self):
        bitsizes = [8, 16, 24, 32]
        blends = ['BLEND_ADD',
                  'BLEND_SUB',
                  'BLEND_MULT',
                  'BLEND_MIN',
                  'BLEND_MAX']
        for bitsize in bitsizes:
            surf = self._make_surface(bitsize)
            comp = self._make_surface(bitsize)
            for blend in blends:
                self._fill_surface(surf)
                self._fill_surface(comp)
                comp.blit(surf, (3, 0),
                          special_flags=getattr(pygame, blend))
                surf.blit(surf, (3, 0),
                          special_flags=getattr(pygame, blend))
                self._assert_same(surf, comp)

    def test_blend_rgba(self):
        bitsizes = [16, 32]
        blends = ['BLEND_RGBA_ADD',
                  'BLEND_RGBA_SUB',
                  'BLEND_RGBA_MULT',
                  'BLEND_RGBA_MIN',
                  'BLEND_RGBA_MAX']
        for bitsize in bitsizes:
            surf = self._make_surface(bitsize, srcalpha=True)
            comp = self._make_surface(bitsize, srcalpha=True)
            for blend in blends:
                self._fill_surface(surf)
                self._fill_surface(comp)
                comp.blit(surf, (3, 0),
                          special_flags=getattr(pygame, blend))
                surf.blit(surf, (3, 0),
                          special_flags=getattr(pygame, blend))
                self._assert_same(surf, comp)

    def test_subsurface(self):
        # Blitting a surface to its subsurface is allowed.
        surf = self._make_surface(32, srcalpha=True)
        comp = surf.copy()
        comp.blit(surf, (3, 0))
        sub = surf.subsurface((3, 0, 6, 6))
        sub.blit(surf, (0, 0))
        del sub
        self._assert_same(surf, comp)
        # Blitting a subsurface to its owner is forbidden because of
        # lock conficts. This limitation allows the overlap check
        # in PySurface_Blit of alphablit.c to be simplified.
        def do_blit(d, s):
            d.blit(s, (0, 0))
        sub = surf.subsurface((1, 1, 2, 2))
        self.failUnlessRaises(pygame.error, do_blit, surf, sub)
        

if __name__ == '__main__':
    unittest.main()
