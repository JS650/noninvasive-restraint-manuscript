%% fileSkimmer.m
% fileSkimmer(directory, files, file_ext) returns a cell array of all files
% in the specified directory (enter full directory path) with a specific
% file extension. Leave file_ext as '' to get all files. Each file is
% outputted following its corresponding full path.
%
% directory -> Str : Starting directory to skim files
% files -> cell array : Starts as empty cell {}
% file_ext -> Str: specify the extension of the files to get. Leave as ''
%
% REQUIREMENTS:
%   Add fileSkimmer to path using addpath(<path-to-fileSkimmer.m>).
%   This script uses recursion and changes the current directory, so it
%   must be added to the path to avoid erroring.
%
% Sam Laxer on May 2, 2022

function fileInfo = fileSkimmer(directory, files, file_ext)

% save current directory to variable to return to after function is run
currendDir = pwd;

% Go to desired directory to begin file skimming
cd(directory);

% Get all folders in current directory
dir_info_raw = dir;
% Save all the file/folder names in current directory to variable
names_raw = {dir_info_raw.name};
paths_raw = {dir_info_raw.folder};

dir_info_counter = 1;
names = {};
% Remove any files beginning with '.' from the 'names' variable
for i = 1:length(dir_info_raw)
    if strcmp(names_raw{i}(1), '.')
        % Here we are assuming that all the files beginning with '.' come
        % before any of the other (valid) files
    
    else
        dir_info(dir_info_counter) = dir_info_raw(i);
        names(dir_info_counter) = names_raw(i);
        paths(dir_info_counter) = paths_raw(i);
        dir_info_counter = dir_info_counter + 1;    
    end
end

for i = 1:length(names)

    % If this is a folder
    if dir_info(i).isdir
        % Recurse: perform directoryskimmer function on sub folders
        files = fileSkimmer(names{i}, files, file_ext);

    % If this is a file
    elseif isfile(names{i})
        % Get current file name
        filename = names{i};
        pathname = [paths{i}, '/'];
        
        if isempty(file_ext) || ((length(filename) > length(file_ext)) && strcmp(filename(end-(length(file_ext)-1):end), file_ext))
            idx = length(files) + 1;
            files{idx} = [pathname, filename];
        end

    end

end

cd ..

fileInfo = files;

% Return to directory prior to this function being run:
cd(currendDir);

end



