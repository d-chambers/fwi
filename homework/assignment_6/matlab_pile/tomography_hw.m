%
% tomography_hw.m
%
% Template function for Ge162 (J. Tromp), homework set on seismic
% tomography and inverse methods.
%
% This program requires that you have pre-computed the design matrix and
% loaded the pertinent data.
%
%
% calls xxx
% called by xxx
%

clear
close all
format short
format compact

colors;

ax1 = [-121 -114 31 37];        % lon-lat plotting dimensions

%=======================================================================
% LOAD DATA

% load sources
[slon,slat,sind] = textread('events_lonlat.dat','%f%f%f','headerlines',1);
nsrc = length(slat);

% load receivers
[rlon,rlat,rind] = textread('recs_lonlat.dat','%f%f%f','headerlines',1);
nrec = length(rlat);

% load spline centers
[qlon,qlat] = textread('con_lonlat_q08.dat','%f%f','headerlines',0);
nspline = length(qlat);

%=======================================================================
% lon-lat gridpoints for plotting

numx = 100;
[lonplot,latplot] = gridvec(ax1(1),ax1(2),numx,ax1(3),ax1(4));
nplot = length(lonplot);

% Compute design matrix for expanding a function in terms of splines;
% this is needed to view the tomographic models that we generate at the end.
B = zeros(nplot,nspline);
for ii=1:nspline
    ff = spline_vals(qlon(ii),qlat(ii),q,lonplot,latplot,{1});
    B(:,ii) = ff(:);
end

%-----------------------------------------
% INVERSE PROBLEM HERE


%======================================================
