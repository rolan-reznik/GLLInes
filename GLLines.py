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
                              varying vec2 normal;
                              varying vec2 widthVarying;

                              void main() {
                               // transform the vertex position
                               vec2 dir = gl_Normal.xy * width.xy;
                               vec4 offset = vec4(dir, 0.0, 0.0);
                               gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex + offset;
                               color = gl_Color;
                               normal = gl_Normal.xy;
                               widthVarying = width;
                            }
                              '''],
            ['''
                #version 120
                varying vec4 color;
                varying vec2 widthVarying;
                varying vec2 normal;
                uniform float feather;
                void main() {
                    // write out the pixel
                    vec2 offset = normal * widthVarying;

                    float alpha = color.a * (1.0 - smoothstep(-feather,
                                                               feather,
                                                               (length(offset) - length(widthVarying)) / length(widthVarying)));

                    vec4 color = vec4(color.r * alpha, color.g * alpha, color.b * alpha, alpha);

                    gl_FragColor = color;
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
    
        self.__drawBatch(lineBatch)
        
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
        widthVector = pointMultipliedByScalar(pointNormalized((width, width * aspect)), width)
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
        self.__drawBatch(lineBatch)

    def __drawBatch(self, batch):
        self.shader.bind()
        self.shader.uniformf("feather", self.feather)
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

shader = Shader(['''
void main() {
    // transform the vertex position
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    // pass through the texture coordinate
    gl_TexCoord[0] = gl_MultiTexCoord0;
}
'''], ['''
uniform sampler2D tex0;
uniform vec2 pixel;
 
void main() {
    // retrieve the texture coordinate
    vec2 c = gl_TexCoord[0].xy;
 
    // and the current pixel
    vec3 current = texture2D(tex0, c).rgb;
 
    // count the neightbouring pixels with a value greater than zero
    vec3 neighbours = vec3(0.0);
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2(-1,-1)).rgb, vec3(0.0)));
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2(-1, 0)).rgb, vec3(0.0)));
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2(-1, 1)).rgb, vec3(0.0)));
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2( 0,-1)).rgb, vec3(0.0)));
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2( 0, 1)).rgb, vec3(0.0)));
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2( 1,-1)).rgb, vec3(0.0)));
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2( 1, 0)).rgb, vec3(0.0)));
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2( 1, 1)).rgb, vec3(0.0)));
 
    // check if the current pixel is alive
    vec3 live = vec3(greaterThan(current, vec3(0.0)));
 
    // resurect if we are not live, and have 3 live neighrbours
    current += (1.0-live) * vec3(equal(neighbours, vec3(3.0)));
 
    // kill if we do not have either 3 or 2 neighbours
    current *= vec3(equal(neighbours, vec3(2.0))) + vec3(equal(neighbours, vec3(3.0)));
 
    // fade the current pixel as it ages
    current -= vec3(greaterThan(current, vec3(0.4)))*0.05;
 
    // write out the pixel
    gl_FragColor = vec4(current, 1.0);
}
'''])

 
# create our shader
shader = Shader(['''
void main() {
    // transform the vertex position
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    // pass through the texture coordinate
    gl_TexCoord[0] = gl_MultiTexCoord0;
}
'''], ['''
uniform sampler2D tex0;
uniform vec2 pixel;
 
void main() {
    // retrieve the texture coordinate
    vec2 c = gl_TexCoord[0].xy;
 
    // and the current pixel
    vec3 current = texture2D(tex0, c).rgb;
 
    // count the neightbouring pixels with a value greater than zero
    vec3 neighbours = vec3(0.0);
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2(-1,-1)).rgb, vec3(0.0)));
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2(-1, 0)).rgb, vec3(0.0)));
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2(-1, 1)).rgb, vec3(0.0)));
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2( 0,-1)).rgb, vec3(0.0)));
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2( 0, 1)).rgb, vec3(0.0)));
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2( 1,-1)).rgb, vec3(0.0)));
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2( 1, 0)).rgb, vec3(0.0)));
    neighbours += vec3(greaterThan(texture2D(tex0, c + pixel*vec2( 1, 1)).rgb, vec3(0.0)));
 
    // check if the current pixel is alive
    vec3 live = vec3(greaterThan(current, vec3(0.0)));
 
    // resurect if we are not live, and have 3 live neighrbours
    current += (1.0-live) * vec3(equal(neighbours, vec3(3.0)));
 
    // kill if we do not have either 3 or 2 neighbours
    current *= vec3(equal(neighbours, vec3(2.0))) + vec3(equal(neighbours, vec3(3.0)));
 
    // fade the current pixel as it ages
    current -= vec3(greaterThan(current, vec3(0.4)))*0.05;
 
    // write out the pixel
    gl_FragColor = vec4(current, 1.0);
}
'''])
 
# bind our shader
shader.bind()
# set the correct texture unit
shader.uniformi('tex0', 0)
# unbind the shader
shader.unbind()
 
# create the texture
texture = pyglet.image.Texture.create(window.width, window.height, GL_RGBA)
 
# create a fullscreen quad
batch = pyglet.graphics.Batch()
batch.add(4, GL_QUADS, None, ('v2i', (0,0, 1,0, 1,1, 0,1)), ('t2f', (0,0, 1.0,0, 1.0,1.0, 0,1.0)))
 
# utility function to copy the framebuffer into a texture
def copyFramebuffer(tex, *size):
    # if we are given a new size
    if len(size) == 2:
        # resize the texture to match
        tex.width, tex.height = size[0], size[1]
 
    # bind the texture
    glBindTexture(tex.target, tex.id)
    # copy the framebuffer
    glCopyTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 0, 0, tex.width, tex.height, 0);
    # unbind the texture
    glBindTexture(tex.target, 0)
 
# handle the window resize event
@window.event
def on_resize(width, height):
    glViewport(0, 0, width, height)
    # setup a simple 0-1 orthoganal projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 1, 0, 1, -1, 1)
    glMatrixMode(GL_MODELVIEW)
 
    # copy the framebuffer, which also resizes the texture
    copyFramebuffer(texture, width, height)
 
    # bind our shader
    shader.bind()
    # set a uniform to tell the shader the size of a single pixel
    shader.uniformf('pixel', 1.0/width, 1.0/height)
    # unbind the shader
    shader.unbind()
 
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

    for i in range(0, 10):
        renderer.feather = 1 * i
        renderer.drawLine((20.0 + 40.0 * i, 100.0), (800.0 + 40.0 * i, 400.0), 2.0)
 
# schedule an empty update function, at 60 frames/second
pyglet.clock.schedule_interval(lambda dt: None, 1.0/60.0)
 
# make the window visible
window.set_visible(True)
 
# finally, run the application
pyglet.app.run()