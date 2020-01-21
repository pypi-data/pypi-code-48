#!/usr/bin/python
"""
Program: run.py
Author: Andrew Blair and Robert Hu
Description: A simple Synapse organization and maintenance Python script.
"""

import os
import shutil
import hashlib
import synapseclient
import synapseutils
from synapseclient import Project, Folder, File, Link

class simpleLogin(object):
    """
    A super class to simplePush and simplePull for logging into a Synapse project
    
    Attributes
    ----------
    username : str
        Synapse username
    password : str
        Synapse password
    project : str
        Synapse project name
    
    Methods
    -------
    syn_client()
        Construct a Python client object for the Synapse repository service
    syn_project()
        Construct a Python client for the Synapse project
        
    References
    -------
    https://python-docs.synapse.org/
    """
    
    def __init__(self, username, password, project):
        '''
        Parameters
        ----------
        username : str
            Synapse username
        password : str
            Synapse password
        project : str
            Synapse project name
        '''
        self.syn = synapseclient.Synapse()
        self.syn.login(username, password)

        self.project = Project(project)
        self.project = self.syn.store(self.project)
    
    def syn_client(self):
        '''
        Construct a Python client object for the Synapse repository service
        
        :param: None
        return: Synapse client constructor
        '''
        return self.syn
    
    def syn_project(self):
        '''
        Construct a Python client for the Synapse project
        
        :param: None
        return: Synapse project constructor
        '''
        return self.project

class simplePush(simpleLogin):
    """
    Sync a local machine's updates to Synapse

    Attributes
    ----------
    username : str
        Synapse username
    password : str
        Synapse password
    project : str
        Synapse project

    Methods
    ----------
    check_subdirs(synapse_folder_dict, paths, subdirs)
        Check if a sub-directory is on Synapse and if they are not sync the folder
    check_files(synapse_folder_dict, paths, files)
        Check if a file's md5 has changed and if it has upload the new file
    file_store(file_path, parent_entityID)
        Upload file to Synapse
    push()
        Sync a local machine's data to Synapse but only if a file entity's md5 is different
    """
    def __init__(self, username, password, project):
        super(simplePush, self).__init__(username, password, project)

    def check_subdirs(self, synapse_folder_dict, paths, subdirs):
        '''
        Check if a sub-directory is on Synapse and if they are not sync the folder
        
        :param synapse_folder_dict: keys are the folder name and values are the folder's associated synapse ID
        :param paths: str, path prefix to file
        :param subdirs: list,  strings that are sub-directories
        return synapse_folder_dict: dict,
        '''
        for dirs in subdirs:
            if dirs == '.ipynb_checkpoints':
                shutil.rmtree(paths + '/' + dirs)
            else:
                dir_entityID = self.syn.findEntityId(dirs, parent=synapse_folder_dict[paths.split('/')[-1]])
                if dir_entityID is not None:
                    synapse_folder_dict[dirs] = dir_entityID
                else:
                    folder = Folder(dirs, parent=synapse_folder_dict[paths.split('/')[-1]])
                    folder = self.syn.store(folder)
                    synapse_folder_dict[folder.name] = folder.id
        return synapse_folder_dict
    
    def check_files(self, synapse_folder_dict, paths, files):
        '''
        Check if a file's md5 has changed and if it has upload the new file
        
        :param synapse_folder_dict: dict, keys are the folder name and values are the folder's associated synapse ID
        :param paths: str, path prefix to file
        :param files: str, file name
        return: None
        '''
        for data in files:
            if data == 'SYNAPSE_METADATA_MANIFEST.tsv':
                os.unlink(paths + '/' + data)
            else:
                file_entityID = self.syn.findEntityId(data, parent=synapse_folder_dict[paths.split('/')[-1]])
                if file_entityID is not None:
                    file_entity = self.syn.get(file_entityID, downloadFile=False)
                    local_md5 = synapseclient.utils.md5_for_file(paths + '/' + data).hexdigest()
                    if file_entity.md5 != local_md5:
                        self.file_store(paths + '/' + data, synapse_folder_dict[paths.split('/')[-1]])
                else:
                    self.file_store(paths + '/' + data, synapse_folder_dict[paths.split('/')[-1]])
                    
    def file_store(self, file_path, parent_entityID):
        '''
        Upload file to Synapse
        
        :param file_path: str, path to the file that will be uploaded to Synapse
        :param parent_entityID: str, An id or an object of a Synapse entity that is the parent of the file being uploaded
        return: None
        '''
        file = File(file_path, parent=parent_entityID)
        file = self.syn.store(file)
        
    def push(self):
        '''
        Sync a local machine's data to Synapse but only if a file entity's md5 is different
        
        :param: None
        return: None
        '''
        synapse_folder_dict = {self.project.name :self.project.id}
        for paths, subdirs, files in os.walk(self.project.name):
            if subdirs:
                synapse_folder_dict = self.check_subdirs(synapse_folder_dict, paths, subdirs)
            if files:
                self.check_files(synapse_folder_dict, paths, files)

class simplePull(simpleLogin):
    """
    Creates a project directory, if one is not already present, and syncs Synapse to a users local machine, without overwriting local files.

    Attributes
    ----------
    username : str
        Synapse username
    password : str
        Synapse password
    project : str
        Synapse project

    Methods
    ----------
    pull()
        Sync Synapse to the local machine without overwriting local entitites
    """

    def __init__(self, username, password, project):
        '''
        Parameters
        ----------
        username : str
            Synapse username
        password : str
            Synapse password
        project : str
            Synapse project
        '''
        super(simplePull, self).__init__(username, password, project)

    def pull(self):
        '''
        Sync Synapse to the local machine without overwriting local entitites
        
        :param: None
        return: None
        '''
        if not os.path.exists(self.project['name']): 
            os.makedirs(self.project['name'])
        synapseutils.sync.syncFromSynapse(self.syn, self.project['id'], path=self.project['name'], ifcollision="keep.local")

def push(username, password, project):
    '''
    Push local updates to Synapse

    Parameters
    ----------
    username : str
        Synapse username
    password : str
        Synapse password
    project : str
        Synapse project

    Returns
    -------
    None
    '''
    simplePush(username, password, project).push()

def pull(username, password, project):
    '''
    Pull Synapse updates without overwriting local files

    Parameters
    ----------
    username : str
        Synapse username
    password : str
        Synapse password
    project : str
        Synapse project

    Returns
    -------
    None
    '''
    simplePull(username, password, project).pull()