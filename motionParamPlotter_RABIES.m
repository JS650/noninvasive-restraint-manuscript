%% motionParamPlotter_RABIES.m
%
% motionParamPlotter(fileLocation, inputTR)
%
% Function used to plot the motion parameters from RABIES-generated csv
% files.
% fileLocation can point to EITHER a FD file or a motion parameter file 
% (both are csv files).
%
% If the inputTR (repetition time) is not included, it defaults to 1.5
% seconds.
%
% From the RABIES preproc folder, the motionparam/FD files (fileLocation)
% can be found:
%   motionparams files:  <preproc-dir>/motion_datasink/motion_params_csv
%   FD files:            <preproc-dir>/motion_datasink/FD_csv
%   
%
% Sam Laxer on June 19, 2024


function motionParamPlotter_RABIES(fileLocation, inputTR)

% Set default input arguments if not defined
if exist('inputTR', 'var')
    TR = inputTR;
else
    disp('Assuming TR = 1.5 s ... If this is incorrect, rerun function and specify TR as input argument.')
    TR = 1.5; % [seconds]
end

% Determine if this is motparams file or FD file:
if strcmp(fileLocation(end-9:end), 'params.csv')
    FD_file = false;
elseif strcmp(fileLocation(end-10:end), 'FD_file.csv')
    FD_file = true;
else
    error('Wrong type of file inputted. Must be RABIES-generated motion parameter file or FD file (csv format).')
end

% If it is a parameter file
if ~FD_file

    % Read in file
    data = readtable(fileLocation);

    % Work only with the 6 rigid body parameters
    mov1 = data{:,'mov1'}; % left/right
    mov2 = data{:,'mov2'}; % ant/post
    mov3 = data{:,'mov3'}; % sup/inf
    rot1 = data{:,'rot1'}; % RL-axis
    rot2 = data{:,'rot2'}; % AP-axis
    rot3 = data{:,'rot3'}; % IS-axis

    left_right = mov1;
    post_ant = mov2;
    sup_inf = mov3;
    % Convert rotations from radians to degrees
    R_L_axis = rot1 .* 180 ./ pi; % [degrees]
    A_P_axis = rot2 .* 180 ./ pi; % [degrees]
    I_S_axis = rot3 .* 180 ./ pi; % [degrees]
    

    %% Stats

    % Now we can condense the 6 rigid body motion parameters into one (RMS of
    % displacement OR Addition in Quadrature) as follows:
    %-------
    % RMS Displacement -> sqrt(mean([x; y; z].^2))
    RMS_trans = rms([left_right'; post_ant'; sup_inf']);
    RMS_rot = rms([R_L_axis'; I_S_axis'; A_P_axis']);
    avgRMS_trans = mean(RMS_trans);
    avgRMS_rot = mean(RMS_rot);
    disp(['Average RMS translation: ', num2str(avgRMS_trans)]);
    disp(['Average RMS rotation: ', num2str(avgRMS_rot)]);
    % Standard deviations
    std_RMStrans = std(RMS_trans);
    std_RMSrot = std(RMS_rot);
    disp(['Standard deviation in RMS of all translations: ', num2str(std_RMStrans)]);
    disp(['Standard deviation in RMS of all rotations: ', num2str(std_RMSrot)]);

    % OR mean of add-in-quadrature of the x, y, and z, translations
    quad_trans = sqrt(left_right.^2 + post_ant.^2 + sup_inf.^2);
    quad_rot =  sqrt(R_L_axis.^2 + I_S_axis.^2 + A_P_axis.^2);
    avgQuad_trans = mean(quad_trans);
    avgQuad_rot = mean(quad_rot);
    disp(['Average add-in-quadrature translation: ', num2str(avgQuad_trans)]);
    disp(['Average add-in-quadrature rotation: ', num2str(avgQuad_rot)]);
    % Standard deviations
    std_QuadTrans = std(quad_trans);
    std_QuadRot = std(quad_rot);
    disp(['Standard deviation of Addition in Quadrature of all translations: ', num2str(std_QuadTrans)]);
    disp(['Standard deviation of Addition in Quadrature of all rotations: ', num2str(std_QuadRot)]);


    %% Define variables with each motion parameter dimension:
    LR_um = left_right * 1000;
    PA_um = post_ant * 1000;
    SI_um = sup_inf * 1000;


    %% Plot results

    f = figure;
    f.Position = [10 800 900 600];
    subplot(2,1,1)
    % Translations
    timeAllDims = (1:length(left_right)) * TR;
    plot(timeAllDims, LR_um, 'b') % '* 1000' to express in um
    hold on
    plot(timeAllDims, PA_um, 'g') % '* 1000' to express in um
    plot(timeAllDims, SI_um, 'r') % '* 1000' to express in um
    %plot((1:length(quad_trans)) * TR, quad_trans * 1000, 'k', 'LineWidth', 3) % Euclidean distance (add in quadrature)
    grid on;
    title('Translation', 'FontSize', 20)
    xlabel('Time (s)', 'FontSize', 17)
    %ylabel('mm', 'FontSize', 17)
    ylabel('µm', 'FontSize', 17)
    %legend('Right', 'Posterior', 'Inferior', 'Add in Quadrature', 'Location', 'Best', 'FontSize', 12)
    legend('Right', 'Posterior', 'Inferior', 'Location', 'Best', 'FontSize', 12)


    subplot(2,1,2)
    % Rotations
    plot(timeAllDims, R_L_axis, 'b')
    hold on
    plot(timeAllDims, I_S_axis, 'g')
    plot(timeAllDims, A_P_axis, 'r')
    %plot(timeAllDims, quad_rot, 'k', 'LineWidth', 3)
    grid on;
    title('Rotation', 'FontSize', 20)
    xlabel('Time (s)', 'FontSize', 17)
    ylabel('Degrees', 'FontSize', 17)
    %legend('R-L Axis', 'I-S Axis', 'A-P Axis', 'Add in Quadrature', 'Location', 'Best', 'FontSize', 12)
    legend('R-L Axis', 'I-S Axis', 'A-P Axis', 'Location', 'Best', 'FontSize', 12)


    %%% Euclidean Distance Translations and Rotations:

    f2 = figure;
    f2.Position = [10 75 900 600];
    subplot(2,1,1)
    % Translations
    plot((1:length(quad_trans)) * TR, quad_trans * 1000)
    grid on;
    title('Euclidean Translations', 'FontSize', 20)
    xlabel('Time (s)', 'FontSize', 17)
    ylabel('µm', 'FontSize', 17)
    %legend('Right', 'Posterior', 'Inferior', 'Location', 'Best', 'FontSize', 12)


    subplot(2,1,2)
    % Rotations
    plot((1:length(quad_rot)) * TR, quad_rot)
    grid on;
    title('Euclidean Rotations', 'FontSize', 20)
    xlabel('Time (s)', 'FontSize', 17)
    ylabel('Degrees', 'FontSize', 17)
    %legend('R-L Axis', 'I-S Axis', 'A-P Axis', 'Location', 'Best', 'FontSize', 12)


else % If this is a FD file (i.e., contains mean and max FDs)

    % Read in file
    data = readtable(fileLocation);

    % Work only with the 6 rigid body parameters
    meanFD = data{:,'Mean'};
    maxFD = data{:,'Max'};

    %% Define variables with each motion parameter dimension:
    meanFD_um = meanFD * 1000;
    maxFD_um = maxFD * 1000;


    %% Plot results

    % Mean voxelwise FDs by itself
    f1 = figure;
    f1.Position = [10 800 900 600];
    timeAllDims = (1:length(meanFD_um)) * TR;
    plot(timeAllDims, meanFD_um, 'b')
    grid on;
    title('Mean Voxelwise Framewise Displacements', 'FontSize', 20)
    xlabel('Time (s)', 'FontSize', 17)
    ylabel('µm', 'FontSize', 17)

    % Mean and Max voxelwise FDs
    f = figure;
    f.Position = [10 800 900 600];
    subplot(2,1,1)
    % Mean
    plot(timeAllDims, meanFD_um, 'b')
    grid on;
    title('Mean Voxelwise Framewise Displacements', 'FontSize', 20)
    xlabel('Time (s)', 'FontSize', 17)
    ylabel('µm', 'FontSize', 17)


    subplot(2,1,2)
    % Max
    plot(timeAllDims, maxFD_um, 'b')
    grid on;
    title('Max Voxelwise Framewise Displacements', 'FontSize', 20)
    xlabel('Time (s)', 'FontSize', 17)
    ylabel('µm', 'FontSize', 17)

    % Set y-axis limits of mean subplot same as max subplot for better
    % comparison
    yl = ylim; % Currently, the max subplot is active, so this gets ylim from that subplot
    h = findobj(f, 'type', 'axes');
    set(h(2), 'YLim', yl');
    %set(h(1), 'XLim', new_xlim_for_bottom_axes);

end