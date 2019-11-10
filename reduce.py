#!/usr/bin/env python3
from __future__ import print_function
import glob
import numpy as np
from stvid.stio import fourframe
from stvid.stio import satid
import ppgplot
from stvid.cmap import viridis, fire
from stvid.stars import pixel_catalog
from stvid.extract import inside_selection
from stvid.extract import plot_selection

def compute_cuts(img, lcut=4.0, hcut=6.0):
    zm, zs = np.mean(img), np.std(img)
    return zm-lcut*zs, zm+hcut*zs

def parse_idents(fname):
    try:
       f = open(fname + ".id")
    except OSError:
        print("Cannot open", fname + ".id")
    else:
        lines = f.readlines()
        f.close()

    # Parse identifications
    idents = [satid(line) for line in lines]

    return idents

# Plot selection
def plot_selection(id, x0, y0, dt=1.0, w=10.0):
    dx, dy = id.x1 - id.x0, id.y1 - id.y0
    ang = np.mod(np.arctan2(dy, dx), 2.0*np.pi)
    r = np.sqrt(dx**2 + dy**2)
    drdt = r / (id.t1 - id.t0)
    sa, ca = np.sin(ang), np.cos(ang)

    dx = np.array([-dt, -dt, id.t1 + dt, id.t1 + dt, -dt]) * drdt
    dy = np.array([w, -w, -w, w, w])
    x = ca * dx - sa * dy + x0
    y = sa * dx + ca * dy + y0

    ppgplot.pgline(x, y)
    ppgplot.pgsch(0.8)
    ppgplot.pgptxt(x[0], y[0], ang*180.0/np.pi, 0.0, "%05d" % id.norad)
    ppgplot.pgsch(1.0)
    
    return


if __name__ == "__main__":
    # Set file name
    #fname = "/data2/satobs/video/results/20190723_0/catalog/2019-07-23T22:41:59.466.fits"
    fname = "/data2/satobs/video/results/20190723_0/classfd/2019-07-23T22:02:51.692.fits"
    #fname = "/data2/satobs/video/results/20190822_0/catalog/2019-08-22T21:52:46.965.fits"
    
    # Read four frame
    ff = fourframe(fname)

    # PGPLOT settings
    tr = np.array([-0.5, 1.0, 0.0, -0.5, 0.0, 1.0])
    cmap_l, cmap_r, cmap_g, cmap_b = viridis()
    #cmap_l, cmap_r, cmap_g, cmap_b = fire()
    
    # Open plot
    ppgplot.pgopen("/xs")
    ppgplot.pgpap(12.0, 0.75)
    ppgplot.pgctab(cmap_l, cmap_r, cmap_g, cmap_b, 5, 1.0, 0.5)
    ppgplot.pgsfs(2)

    # Initial settings
    nx, ny = ff.nx, ff.ny
    wx, wy = float(nx), float(ny)
    xmin, xmax = 0, nx
    ymin, ymax = 0, ny
    layer = 3
    redraw = True
    plotstars = False
    plotsats = False
    applymask = True
    trackid = 99999

    trksig = 5.0
    trkrmin = 10.0
    
    p = pixel_catalog(fname + ".cat")

    idents = parse_idents(fname)

    if applymask:
        mask = ff.zsig>trksig
    else:
        mask = np.ones_like(ff.zavg)    
    
    # Forever loop
    while True:
        # Redraw plot
        if redraw:
            # Initialize
            ppgplot.pgeras()
            ppgplot.pgsvp(0.1, 0.99, 0.1, 0.95)
            ppgplot.pgswin(xmin, xmax, ymin, ymax)

            # Select layer
            if layer==1:
                img = ff.zavg
            elif layer==2:
                img = ff.zstd
            elif layer==3:
                img = ff.zmax
            elif layer==4:
                img = ff.znum
            elif layer==5:
                img = (ff.zmax-ff.zavg)/(ff.zstd+1e-9)

            # Determine cuts
            if layer==4:
                zmin, zmax = np.min(img), np.max(img)
            else:
                zmin, zmax = compute_cuts(img)

            # Plot image
            #ppgplot.pgimag(img*mask, nx, ny, 0, nx-1, 0, ny-1, zmax, zmin, tr)
            ppgplot.pggray(img*mask, nx, ny, 0, nx-1, 0, ny-1, zmax, zmin, tr)
            ppgplot.pgbox("BCTSNI", 0., 0, "BCTSNI", 0., 0)

            # Plot stars
            if plotstars:
                ppgplot.pgsci(2)
                ppgplot.pgpt(p.x, p.y, 4)
                ppgplot.pgsci(1)

            # Plot satellites
            if plotsats:
                for ident in idents:
                    if "catalog" in ident.catalog:
                        ppgplot.pgsci(0)
                    elif "classfd" in ident.catalog:
                        ppgplot.pgsci(4)
                    elif "unidentified" in ident.catalog:
                        ppgplot.pgsci(8)
                    ppgplot.pgpt1(ident.x0, ident.y0, 17)
                    ppgplot.pgmove(ident.x0, ident.y0)
                    ppgplot.pgdraw(ident.x1, ident.y1)


            # Plot selections
            for ident in idents:
                if "unidentified" in ident.catalog:
                    ppgplot.pgsci(7)
                    plot_selection(ident, ident.x0, ident.y0)
                    ppgplot.pgsci(1)

            # Track object
            if trackid is not None:
                for ident in idents:
                    if ident.norad == trackid:
                        break
                x, y, t, sig = ff.significant_pixels_along_track(trksig, ident.x0, ident.y0, ident.dxdt, ident.dydt, trkrmin)

                print(x, y, t, sig)

            redraw = False

        print("here")
        # Read cursor
        x, y, char = ppgplot.pgcurs()

        print(x, y, char)
        
        # Quit
        if char == b"q":
            break

        # Toggle layers
        if char.isdigit():
            layer = int(char)
            redraw = True
            continue

        # Center
        if char == b"c":
            xmin, xmax = x-0.5*wx, x+0.5*wx
            ymin, ymax = y-0.5*wy, y+0.5*wy
            redraw = True
            continue
        
        # Zoom
        if char == b"z":
            wx /= 1.25
            wy /= 1.25
            xmin, xmax = x-0.5*wx, x+0.5*wx
            ymin, ymax = y-0.5*wy, y+0.5*wy
            redraw = True
            continue

        # Unzoom
        if char == b"x":
            wx *= 1.25
            wy *= 1.25
            xmin, xmax = x-0.5*wx, x+0.5*wx
            ymin, ymax = y-0.5*wy, y+0.5*wy
            redraw = True
            continue

        # Reset
        if char == b"r":
            xmin, xmax = 0, nx
            ymin, ymax = 0, ny
            wx, wy = float(nx), float(ny)
            redraw = True
            continue

        # Plot stars
        if char == b"P":
            plotstars = not plotstars
            redraw = True
            continue

        # Plot satellites
        if char == b"p":
            plotsats = not plotsats
            redraw = True
            continue

        # Mask
        if char == b"m":
            applymask = not applymask
            if applymask:
                mask = ff.zsig>trksig
            else:
                mask = np.ones_like(ff.zavg)
            redraw = True
            continue

        
    ppgplot.pgend()
