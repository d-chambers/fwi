%
% compute_Gik_ray.m
%
% Template function for Ge162 (J. Tromp), homework set on seismic
% tomography and inverse methods.
%
% calls xxx
% called by xxx
%

format short
format compact
close all
clear

%-----------------------------

ax1 = [-120.157113 -114.809623 32 36.364429];
lonmin = ax1(1); lonmax = ax1(2);
latmin = ax1(3); latmax = ax1(4);
colors;

%-----------------------------
% LOAD DATA

% load sources
[slons,slats,sinds] = textread('events_lonlat.dat','%f%f%f','headerlines',1);
nsrc = length(slats);

% load receivers
[rlons,rlats,rinds] = textread('recs_lonlat.dat','%f%f%f','headerlines',1);
nrec = length(rlats);

% load spline centers
[qlons,qlats] = textread('con_lonlat_q08.dat','%f%f','headerlines',0);
nspline = length(qlats);

figure; hold on;
plot(qlons,qlats,'.');
text(qlons,qlats,num2str([1:nspline]'),'fontsize',6); % only seen when printed/saved
axis equal, axis(ax1);
xlabel(' Longitude'); ylabel(' Latitude');
title(' Center-points of spherical spline basis functions');
fontsize(10); orient tall, wysiwyg

% load reference velocity
% THIS MAY BE DIFFERENT FROM ONE MODEL TO THE NEXT
temp = load('socal_vel_c0.dat');
c0 = temp(1);

%-----------------------------
% compute ray paths (great circles)

% spline evaluations
opts = {1};
q = 8;

% number of points along each ray path
nump = 1000;

% test the ordering scheme for the rows of G
if (1==1)
    %i = 0;
    disp('     i   isrc  irec ');
    for isrc = 1:nsrc
        for irec = 1:nrec
            %i = i+1;
            i = (isrc-1)*nrec + irec;
            disp(sprintf('%6i%6i%6i',i,isrc,irec));
        end
    end
end

% compute design matrix






% save design matrix
%save([outdir 'Amat_ray'],'Amat_ray');

%=====================================================================
