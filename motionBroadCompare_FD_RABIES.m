%% motionBroadCompare_FD_RABIES.m
%
% Broadly analyze motion of multiple runs.
%
% Created by Sam Laxer on June 4, 2024

close all
clear variables

%% Read in motionparam files

% Path to RABIES-generated FD_csv file:
FD_csv_path = '/Volumes/menon_data$/slaxer/data/ds-NonInvasiveImg/derivatives/rabies_NoninvasiveAndHeadpost/FromAllianceCan/preproc6_robust/motion_datasink/FD_csv';

% Find all FD_csv files
FD_csv_files = fileSkimmer(FD_csv_path, {}, '.csv');

% Go through each file and save all mean and max FDs
all_mean_FDs = nan(600,length(FD_csv_files));
all_max_FDs = nan(600,length(FD_csv_files));

for file = 1:length(FD_csv_files)%[9:168, 175:length(FD_csv_files)]
    fprintf([num2str(file), '\t', FD_csv_files{file}, '\n']);
    data = readtable(FD_csv_files{file});
    all_mean_FDs(1:height(data),file) = data{:,'Mean'};
    all_max_FDs(1:height(data),file) = data{:,'Max'};
end


%% Stats

% Mean and SD of mean FD for each run:
mean_all_mean_FDs = mean(all_mean_FDs, 'omitnan');
std_all_mean_FDs = std(all_mean_FDs, 'omitnan');
% Mean and SD of max FD for each run:
mean_all_max_FDs = mean(all_max_FDs, 'omitnan');
std_all_max_FDs = std(all_max_FDs, 'omitnan');


%% Global average and standard deviation

globalavg = mean(all_mean_FDs, 'all', 'omitnan');
globalstd = std(all_mean_FDs, 0, 'all', 'omitnan');
fprintf('The global mean framewise displacement is %g mm and global standard deviation is %g mm\n', globalavg, globalstd);

global_FDavg = mean(all_max_FDs, 'all', 'omitnan');
global_FDstd = std(all_max_FDs, 0, 'all', 'omitnan');
fprintf('The global mean max framewise displacement is %g mm and global standard deviation is %g mm\n', global_FDavg, global_FDstd);


%%
%% Define plotting parameters
%%

errbarColor = 'k';
errbarMarkers = 'o';
errbarMarkers_m = 'o';
errbarMarkers_f = 'o';
linetype_m = '-';
linetype_f = '--';

xlim_margin = 0.15; % margin (in %) of the x range that is displayed (x-axis limits)
xticklabels_4day = {'Day 1', 'Day 2', 'Day 4'};
xticklabels_9day = {'Day 1', 'Day 2', 'Day 4', 'Day 9'};
xticklabels_13day = {'Day 1', 'Day 2', 'Day 4', 'Day 9', 'Day 13'};

lwm = 1; % LineWidth for markers
lwl = 2; % LineWdith for lines
mColor = 'k'; % MarkerFaceColor for combined males and females
mColor_m = 'k'; % MarkerFaceColor for males
mColor_f = 'k'; % MarkerFaceColor for females
mSize_line = 5; % MarkerSize for lines
mSize_marker = 5; % MarkerSize for markers
cSize = 15; % Error bar cap sizes

axesTickLength = [0.03, 0.03]; % Length of ticks on axes
axesFontSize = 20; % Fond size for axes numbers
axesFontWeight = 'bold';
axes_lw = 2; % Axes LineWidth
axes_Color = 'none'; % Background fill color of plot

title_fs = 20; % Title font size
title_fw = 'bold'; % Title font weight
label_fs = 20; % x- and y-label font size
label_fw = 'bold'; % x- and y-label font weight

legend_loc = 'northeastoutside'; % Legend location


%% Plot (Displacements vs Run #)

% Average Mean Voxelwise FDs for each run
figure
errorbar(1:length(mean_all_mean_FDs), mean_all_mean_FDs, std_all_mean_FDs)
hold on;
%plot([0 250], [0.3 0.3], '--r')
title('Average Mean Voxelwise Displacements vs Run #');
xlabel('Run #');
ylabel('Average Mean Voxel Displacement [mm]');

% Average Max Voxelwise FDs for each run
figure
errorbar(1:length(mean_all_max_FDs), mean_all_max_FDs, std_all_max_FDs)
title('Average Max Voxelwise Displacements vs Run #');
xlabel('Run #');
ylabel('Average Max Voxel Displacement [mm]');


%% Histogram of Displacements

figure
histogram(all_mean_FDs);
hold on;
plot([0.15 0.15], [0 9000], '--r')
title(['Total Count: ', num2str(nnz(~isnan(all_mean_FDs)))])
xlabel('Mean Displacements (mm)');
ylabel('Count')
set(gca,'TickDir','out', 'TickLength', axesTickLength, 'FontSize', axesFontSize, 'FontWeight', axesFontWeight, 'LineWidth', axes_lw, 'Color', axes_Color);



figure
histogram(all_max_FDs);
hold on;
plot([0.3 0.3], [0 10000], '--r')
title(['Total Count: ', num2str(nnz(~isnan(all_max_FDs)))])
xlabel('Maximum Displacements (mm)');
ylabel('Count')

