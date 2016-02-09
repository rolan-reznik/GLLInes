# Based on
# Copyright Tristam Macdonald 2008.
#
# Distributed under the Boost Software License, Version 1.0
# (see http://www.boost.org/LICENSE_1_0.txt)
#

import pyglet
import pyglet.info
from pyglet.gl import *

import math
from GLLMath import *
 
from shader import Shader

class LineRendererDynamic:
    def __init__(self):
        self.feather = 0.4
        self.shader = Shader(['''
                              #version 120
                              attribute vec2 width;
                              varying vec4 color;
                              varying vec2 offset;

                              void main() {
                               // transform the vertex position
                               vec2 dir = gl_Normal.xy * width.xy;
                               offset = dir;
                               gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex + vec4(offset, 0.0, 0.0);
                               color = gl_Color;
                            }
                              '''],
            ['''
                #version 120
                varying vec4 color;
                varying vec2 offset;
                uniform float feather;
                uniform float width;

                void main() {
                    vec4 newColor = color;
                    //if (length(offset) >= width * 0.9) {
                    //    newColor = vec4(1.0, 0.0, 0.0, 1.0);
                    //}

                    float alpha = 1.0 - smoothstep(-width * feather, width * feather, length(offset) - width);

                    newColor = vec4(color.r * alpha, color.g * alpha, color.b * alpha, alpha);

                    gl_FragColor = newColor;
                }
             '''])
        
    def drawLineInNormalizedCoordinates(self, start, end, width):
        lineBatch = pyglet.graphics.Batch()
    
        direction = pointsSubtract(end, start)
        cross = pointNormalized(pointCross(direction))
        cross = (cross[0], cross[1] * (window.width / window.height))
        crossAlt = pointNormalized(pointCrossAlt(direction))
        crossAlt = (crossAlt[0], crossAlt[1] * (window.width / window.height))
        
        aspect = window.width / window.height
        widthVector = pointsMultiply(pointNormalized((width, width * aspect)), width)
        vertex_list = lineBatch.add(
            6,
                                    pyglet.gl.GL_TRIANGLES,
                                    None,
                                    ('v2f',
                                     (start[0], start[1], end[0], end[1], start[0], start[1],
                                      start[0], start[1], end[0], end[1], end[0], end[1])
                                    ),
                                    ('c4f',
                                     (1.0, 0.0, 0.0, 1.0,  1.0, 0.0, 0.0, 0.5,  1.0, 0.0, 0.0, 0.5,
                                      
                                      0.0, 1.0, 0.0, 1.0,  0.0, 0.0, 1.0, 1.0,  0.0, 0.0, 1.0, 1.0)
                                    ),
                                    ('n3f',
                                     (cross[0], cross[1], 1.0,  crossAlt[0], crossAlt[1], 1.0,  crossAlt[0], crossAlt[1], 1.0,
                                      cross[0], cross[1], 1.0, cross[0], cross[1], 1.0,  crossAlt[0], crossAlt[1], 1.0)
                                     )
                                    ,
                                    ('1g2f',
                                     (widthVector[0], widthVector[1],  widthVector[0], widthVector[1],  widthVector[0], widthVector[1],
                                      
                                      widthVector[0], widthVector[1],  widthVector[0], widthVector[1],  widthVector[0], widthVector[1])
                                    )
                                    )
    
        self.__drawBatch(lineBatch, widthVector[0])
        
    def drawLine(self, start, end, width):
        lineBatch = pyglet.graphics.Batch()
        
        start = pointsDivide(start, (window.width, window.height))
        end = pointsDivide(end, (window.width, window.height))
        
        direction = pointsSubtract(end, start)
        cross = pointNormalized(pointCross(direction))
        cross = (cross[0], cross[1] * (window.width / window.height))
        cross = pointNormalized(cross)
        crossAlt = pointNormalized(pointCrossAlt(direction))
        crossAlt = (crossAlt[0], crossAlt[1] * (window.width / window.height))
        crossAlt = pointNormalized(crossAlt)

        #since in veretx shader coordinates ar maped into device normalized space we do not need to divide width by half
        width = width / window.width
        
        aspect = window.width / window.height
        widthVector = (width, width) #pointMultipliedByScalar(pointNormalized((width, width * aspect)), width)
        vertex_list = lineBatch.add(
            6,
                                    pyglet.gl.GL_TRIANGLES,
                                    None,
                                    ('v2f',
                                     (start[0], start[1], end[0], end[1], start[0], start[1],
                                      start[0], start[1], end[0], end[1], end[0], end[1])
                                    ),
                                    ('c4f',
                                     (1.0, 1.0, 1.0, 1.0,  1.0, 1.0, 1.0, 1.0,  1.0, 1.0, 1.0, 1.0,
                                      
                                      1.0, 1.0, 1.0, 1.0,  1.0, 1.0, 1.0, 1.0,  1.0, 1.0, 1.0, 1.0)
                                    ),
                                    ('n3f',
                                     (cross[0], cross[1], 1.0,  crossAlt[0], crossAlt[1], 1.0,  crossAlt[0], crossAlt[1], 1.0,
                                      cross[0], cross[1], 1.0, cross[0], cross[1], 1.0,  crossAlt[0], crossAlt[1], 1.0)
                                     )
                                    ,
                                    ('1g2f',
                                     (widthVector[0], widthVector[1],  widthVector[0], widthVector[1],  widthVector[0], widthVector[1],

                                      widthVector[0], widthVector[1],  widthVector[0], widthVector[1],  widthVector[0], widthVector[1])
                                    )
                                   )
        self.__drawBatch(lineBatch, widthVector[0])

    def __drawBatch(self, batch, width):
        self.shader.bind()
        self.shader.uniformf("feather", self.feather)
        self.shader.uniformf("width", width)
        batch.draw()
        self.shader.unbind()

    
class LineRendererAliased:
    
    def DrawLineInNormalizedCoordinates(self, start, end, width):
            lineBatch = pyglet.graphics.Batch()
    
            direction = pointsSubtract(end, start)
            cross = pointNormalized(pointCross(pointNormalized(direction)))
            cross = (cross[0], cross[1] * (window.width / window.height))
            
            widthPoint = (width, width * window.width / window.height)
            
            halfCross = pointsMultiply(pointMultipliedByScalar(widthPoint, 0.5), cross)
            
            tl = pointsAdd(start, halfCross)
            tr = pointsAdd(start, pointsAdd(direction, halfCross))
            halfCross = pointsMultiply(pointMultipliedByScalar(widthPoint, -0.5), cross)
            bl = pointsAdd(start, halfCross)
            br = pointsAdd(start, pointsAdd(direction, halfCross))
            
            vertex_list = lineBatch.add(
                6,
                                        pyglet.gl.GL_TRIANGLES,
                                        None,
                                        ('v2f',
                                         (tl[0], tl[1], tr[0], tr[1], bl[0], bl[1],
                                          tr[0], tr[1], br[0], br[1], bl[0], bl[1])
                                        ),
                                        ('c4f',
                                         (1.0, 1.0, 1.0, 1.0,  1.0, 1.0, 1.0, 1.0,  1.0, 1.0, 1.0, 1.0,
                                          1.0, 1.0, 1.0, 1.0,  1.0, 1.0, 1.0, 1.0,  1.0, 1.0, 1.0, 1.0))
                                        )
            lineBatch.draw()
        
    
    def drawLine(self, start, end, width):
            lineBatch = pyglet.graphics.Batch()
    
            direction = pointsSubtract(end, start)
            cross = pointNormalized(pointCross(pointNormalized(direction)))
            
            halfCross = pointMultipliedByScalar(cross, width * 0.5)
            
            tl = pointsAdd(start, halfCross)
            tr = pointsAdd(start, pointsAdd(direction, halfCross))
            halfCross = pointMultipliedByScalar(cross, width * -0.5)
            bl = pointsAdd(start, halfCross)
            br = pointsAdd(start, pointsAdd(direction, halfCross))
            
            tl = pointsDivide(tl, (window.width, window.height))
            tr = pointsDivide(tr, (window.width, window.height))
            bl = pointsDivide(bl, (window.width, window.height))
            br = pointsDivide(br, (window.width, window.height))
        
            vertex_list = lineBatch.add(
                6,
                                        pyglet.gl.GL_TRIANGLES,
                                        None,
                                        ('v2f',
                                         (tl[0], tl[1], tr[0], tr[1], bl[0], bl[1],
                                          tr[0], tr[1], br[0], br[1], bl[0], bl[1])
                                        ),
                                        ('c4f',
                                         (1.0, 1.0, 1.0, 1.0,  1.0, 1.0, 1.0, 1.0,  1.0, 1.0, 1.0, 1.0,
                                          1.0, 1.0, 1.0, 1.0,  1.0, 1.0, 1.0, 1.0,  1.0, 1.0, 1.0, 1.0))
                                        )
            lineBatch.draw()
        

# create the window, but keep it offscreen until we are done with setup
window = pyglet.window.Window(1024, 768, resizable=True, visible=False, caption="Lines")
 
# centre the window on whichever screen it is currently on (in case of multiple monitors)
window.set_location(window.screen.width/2 - window.width/2, window.screen.height/2 - window.height/2)

# handle the window resize event
@window.event
def on_resize(width, height):
    glViewport(0, 0, width, height)
    # setup a simple 0-1 orthoganal projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 1, 0, 1, -1, 1)
    glMatrixMode(GL_MODELVIEW)
 
    # tell pyglet that we have handled the event, to prevent the default handler from running
    return pyglet.event.EVENT_HANDLED
 
# clear the window and draw the scene
@window.event
def on_draw():
    # pyglet.info.dump_gl()
    # clear the screen
    window.clear()
    
    glClearColor(0, 0, 0, 0);
    glClear(GL_COLOR_BUFFER_BIT)
    glEnable(GL_BLEND)
    glBlendEquation(GL_FUNC_ADD)
    glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
    # 
    # aliasedRenderer = LineRendererAliased()
    # # aliasedRenderer.drawLine((10, 200), (500, 700), 40.0)
    # aliasedRenderer.DrawLineInNormalizedCoordinates((0.1, 0.1), (0.9, 0.8), 40.0 / 768.0)
    
    renderer = LineRendererDynamic()
    # dynamicRenderer.drawLineInNormalizedCoordinates((0.1, 0.1), (0.9, 0.9), 40 / 768.0)

    # renderer.drawLine((20.0, 100.0), (800.0, 100.0), 4.0)

    for i in range(0, 25):
        renderer.feather = i * 0.05
        renderer.drawLine((20.0, 500.0 - 20.0 * i), (800.0, 800.0 - 20.0 * i), 3.0)
 
# schedule an empty update function, at 60 frames/second
pyglet.clock.schedule_interval(lambda dt: None, 1.0/60.0)
 
# make the window visible
window.set_visible(True)
 
# finally, run the application
pyglet.app.run()