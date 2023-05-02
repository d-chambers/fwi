function ff = spline_vals(clon, clat, q, lon_vec, lat_vec, opts)

% convert to theta-phi
deg    = 180/pi;
ph     = clon/deg;
th     = (90-clat)/deg;
ph_vec = lon_vec/deg;
th_vec = (90-lat_vec)/deg;

% options and parameters -- q controls the scale (width) of the spline
ncol  = opts{1};      % number of columns of ff to return
nf    = 2^q;
c72   = cos(72/deg);
base  = acos(c72 / (1 - c72));
db    = base / nf;
zeps  = 1e-3*base;     % determines whether a datapoint is ON a gridpoint

% datapoint locations
costh = cos(th_vec);
sinth = sin(th_vec);
ndata = length(th_vec);

% r : delta/delta-bar in WD95
del = acos( cos(th) * costh + sin(th) * sinth .* cos(ph - ph_vec) );
r   = del/ db;
dif = r - 1;

% separate r into three parts: assign each element to one of four regions
inds1 = find( dif > 1 );                    % outside outer circle
inds2 = find( and( dif <= 1, dif >= 0 ));   % within outer ring
inds3 = find( and( dif > -1 + zeps, dif < 0 ));    % within inner circle
inds4 = find( dif <= -1 + zeps );           % ON the center point

% check
if sum([ length(inds1) length(inds2) length(inds3) length(inds4)]) - length(dif) ~= 0
    length(inds1), length(inds2), length(inds3), length(inds4)
    sum([ length(inds1) length(inds2) length(inds3) length(inds4)]), length(dif)
    error('datapoints have not been partitioned properly');
end

if ncol == 1

    ff = zeros(ndata,1);
    ff(inds2) = ((-0.25*dif(inds2)  + 0.75).*dif(inds2)  - 0.75).*dif(inds2) + 0.25;
    ff(inds3) = (0.75*r(inds3) - 1.5) .* r(inds3).^2  + 1;
    ff(inds4) = 1;

else

    cosdel = cos(th)*costh + sin(th) * sinth .* cos(ph - ph_vec);
    sindel = sqrt(1 - cosdel.*cosdel);
    cotdel = cosdel ./ sindel;

    % delta: arc-distance from test-point to gridpoints
    %adist = acos(cosdel);

    % ddelta/dphi and ddelta/dtheta (see MMA file wang_arc.nb)
    dadp = ( sin(th) * sinth .* sin(ph_vec - ph) ) ./ sindel;
    dadt = ( cos(th) * sinth - costh * sin(th) .* cos(ph - ph_vec) ) ./ sindel;

    % db : delta-bar in WD95
    % d_near varies for each gridpoint, due to irregularities in grids
    %dq = 1 / (db*dnear);
    dq = 1 / db;

    % delta/delta-bar in WD95
    %r = dq * adist;

    % columns of ff :
    % (1) f, function value
    % (2) df/dph
    % (3) df/dth
    % (4) surf_del2 -- depends only on delta
    % (5) |del f|   -- depends only on delta

    % datapoint is outside the outer circle
    ff = zeros(ndata,ncol);

    % datapoint is within the outer ring
    ff(inds2,1) = ((-0.25*dif(inds2) + 0.75).*dif(inds2) - 0.75) .* dif(inds2) + 0.25;
    ff(inds2,2) = dq * (-0.75 + 1.5*dif(inds2) - 0.75*dif(inds2).^2) .* dadp(inds2);
    ff(inds2,3) = dq * (-0.75 + 1.5*dif(inds2) - 0.75*dif(inds2).^2) .* dadt(inds2);
    if ncol >= 4
    ff(inds2,4) = dq * (3 - 1.5*r(inds2) + cotdel(inds2) .* ...
                      (-0.75 + 1.5*dif(inds2) - 0.75*dif(inds2).^2));
    ff(inds2,5) = 0.75 * db^-3 * (2*db - del(inds2)).^2;
    end


    % datapoint is within the inner circle
    ff(inds3,1) = (0.75*r(inds3) - 1.5) .* (r(inds3).^2) + 1;
    ff(inds3,2) = dq * (-3*r(inds3) + 2.25*r(inds3).^2) .* dadp(inds3);
    ff(inds3,3) = dq * (-3*r(inds3) + 2.25*r(inds3).^2) .* dadt(inds3);
    if ncol >= 4
    ff(inds3,4) = dq * (-3 + 4.5*r(inds3) + cotdel(inds3) .* (-3*r(inds3) + 2.25*r(inds3).^2));

    ff(inds3,5) = 0.75 * db^-3 * (4*db - 3*del(inds3)) .* del(inds3);
    end

    % datapoint is in the vicinity of the target spline centerpoint
    % FIX THIS : see Wang & Dahlen (1995)
    % here we simply assign it the closest value
    if length(inds4) > 0
        if ncol > 3
            igood = find( dif > -1 + zeps );
            imin  = min(r(igood));
            d2val = ff(imin,4);
            tvec = zeros(1,ncol);
            tvec(1) = 1;
            tvec(end) = d2val;
            ff(inds4,1) = repmat( tvec, length(inds4), 1 );

        elseif ncol == 3
            ff(inds4,1:3) = [1 0 0];

        elseif ncol == 1
            ff(inds4,1) = 1;
        end
    end

end
