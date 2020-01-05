#!/usr/bin/env python3
import numpy as np
import time
import matplotlib.pyplot as plt
from stvid.stio import fourframe
from astropy.time import Time
from astropy.wcs import WCS
import astropy._erfa as erfa
import astropy.units as u
from astropy.coordinates import SkyCoord
from cysgp4 import PyTle, PyObserver, propagate_many

def rotation_matrix(theta, axis):
    # Angles
    ct, st = np.cos(theta), np.sin(theta)
    zeros, ones = np.zeros_like(theta), np.ones_like(theta)
    if axis == "x":
        R = np.array([[ones, zeros, zeros], [zeros, ct, -st], [zeros, st, ct]])
    elif axis == "y":
        R = np.array([[ct, zeros, st], [-st, zeros, ct], [zeros, ones, zeros]])
    elif axis == "z":
        R = np.array([[ct, -st, zeros], [st, ct, zeros], [zeros, zeros, ones]])

    return np.moveaxis(R, 2, 0)

def teme_to_gcrs(t, pteme, vteme):
    # Equation of the equinoxes
    eqeq = erfa.ee00a(t.tt.jd, 0.0)
    Req = rotation_matrix(eqeq, "z")

    # Precession, nutation and bias
    Rpnb = erfa.pnm00a(t.tt.jd, 0.0)

    # Multiply matrices (take transpose of Rpnb)
    R = np.einsum("...ij,...kj->...ik", Req, Rpnb)

    # Multiply vectors
    pgcrs = np.einsum("i...jk,i...k->i...j", R, pteme)
    vgcrs = np.einsum("i...jk,i...k->i...j", R, vteme)
    
    return pgcrs, vgcrs

def lle_to_gcrs(t, lat_deg, lon_deg, elev_m):
    # Compute ITRs position (in km)
    pitrs = erfa.gd2gc(1, lon_deg * np.pi / 180, lat_deg * np.pi / 180, elev_m) / 1000.0

    # Greenwich apparent sidereal time
    theta_gast = erfa.gst00a(t.ut1.jd, 0.0, t.tt.jd, 0.0)
    Rgast = rotation_matrix(theta_gast, "z")

    # Precession, nutation and bias
    Rpnb = erfa.pnm00a(t.tt.jd, 0.0)    

    # Multiply matrices (take transpose of Rpnb)
    R = np.einsum("...ji,...jk->...ik", Rpnb, Rgast)

    # Multiply vector
    if len(pitrs.shape) == 1:
        pgcrs = (R).dot(pitrs)
    else:
        pgcrs = np.einsum("...ij,kj->...ki", R, pitrs)
    
    return pgcrs

def separation(ra0, dec0, dp):
    dp0 = np.array([np.cos(dec0) * np.cos(ra0),
                    np.cos(dec0) * np.sin(ra0),
                    np.sin(dec0)])

    return np.arccos((dp).dot(dp0) / np.linalg.norm(dp, axis=-1))

if __name__ == "__main__":
    fname = "/home/bassa/2019-12-30T17:17:14.981.fits"
    fname = "/data2/satobs/video/20200104_0/catalog/2020-01-04T16:44:47.946.fits"
    
    # Read fourframe
    ff = fourframe(fname)

    # Times
    t = Time(ff.mjd, format="mjd") + np.linspace(0, ff.texp, 10) * u.s
    mjds = t.mjd[:, np.newaxis, np.newaxis]

    # Observer position
    lat_deg, lon_deg, elev_m = 52.8344, 6.3785, 10
    observer = np.array([PyObserver(lon_deg, lat_deg, elev_m)])

    # TLEs
    #for flag, tlefile in enumerate(["/data2/tle/classfd.tle", "/data2/tle/inttles.tle", "/data2/tle/catalog.tle"]):
    for flag, tlefile in enumerate(["/home/bassa/test.txt", "/home/bassa/test2.txt", "/home/bassa/test3.txt"]):
        with open(tlefile, "r") as fp:
            text = fp.read().rstrip()
        lines = text.split("\n")
        tle_list = []
        for i in range(len(lines)):
            if lines[i][0] == "1":
                tle_list.append((lines[i-1], lines[i], lines[i+1]))
        if flag == 0:
            tles = np.array([PyTle(*tle) for tle in tle_list])
            catalogs = flag * np.ones(len(tle_list))
        else:
            tles = np.concatenate((tles, np.array([PyTle(*tle) for tle in tle_list])))
            catalogs = np.concatenate((catalogs, flag * np.ones(len(tle_list))))
            
    satnos = np.array([tle.catalog_number for tle in tles.squeeze()])

    print(tles[0].tle_strings())
    
    # Propagate
    result = propagate_many(t.mjd[:, np.newaxis, np.newaxis],
                            tles[np.newaxis, np.newaxis, :],
                            observer[np.newaxis, :, np.newaxis],
                            on_error="coerce_to_nan", do_eci_pos=True, do_eci_vel=True, do_geo=False, do_topo=False)

    # Extract position and velocity
    psat_teme = result['eci_pos'].squeeze()
    vsat_teme = result['eci_vel'].squeeze()

    # Convert to GCRS
    psat_gcrs, vsat_gcrs = teme_to_gcrs(t, psat_teme, vsat_teme)

    print(psat_teme[0])
    
    # Compute observer position
    pobs_gcrs = lle_to_gcrs(t, lat_deg, lon_deg, elev_m)

    # Compute spherical coordinates
    dp = psat_gcrs - pobs_gcrs[:, np.newaxis, :]
    r = np.sqrt(np.sum(dp**2, axis=-1))
    ra = np.arctan2(dp[:, :, 1], dp[:, :, 0]) * 180 / np.pi
    dec = np.arcsin(dp[:, :, 2] / r) * 180 / np.pi

    
    # Select objects within a certain distance
    c = separation(ff.crval[0] * u.deg, ff.crval[1] * u.deg, dp[0]) * u.rad < 20 * u.deg

    satno = satnos[c]
    catalog = catalogs[c]
    
    tref = Time(ff.mjd, format="mjd", scale="utc") + 0.5 * ff.texp * u.s
    dra = t.sidereal_time("mean", "greenwich") - tref.sidereal_time("mean", "greenwich")

    
    p = SkyCoord(ra=ra[:, c] - dra[:, np.newaxis].to(u.deg).value, dec=dec[:, c], frame="icrs", unit=("deg", "deg"))

    w = ff.w

    # Image stats
    v = ff.zmax
    vmean, vstd = np.mean(v), np.std(v)
    vmin, vmax = vmean-3.0*vstd, vmean+6.0*vstd

    fig, ax = plt.subplots(figsize=(10, 8))

    
    # Plot image
    ax.imshow(v, origin="lower", aspect=1, interpolation="None", cmap="gray",
              vmin=vmin, vmax=vmax)

    x, y = p.to_pixel(w, origin=0, mode="wcs")

    alpha = 0.5

    for i in range(np.sum(c)):
        if catalog[i] == 0:
            color = "b"
        elif catalog[i] == 1:
            color = "g"
        else:
            color = "k"
        ax.plot(x[:, i], y[:, i], color=color, alpha=alpha)
        if x[0, i] > 0 and x[0, i] < ff.nx and y[0, i] > 0 and y[0, i] < ff.ny:
            ax.plot(x[0, i], y[0, i], color=color, marker=".", alpha=alpha)
            ax.text(x[0, i], y[0, i], " %05d" % satno[i], color=color, alpha=alpha)

    ax.set_xlim(0, ff.nx)
    ax.set_ylim(0, ff.ny)
    
    plt.tight_layout()
    plt.show()
    #plt.savefig("satid.png", bbox_inches="tight")
