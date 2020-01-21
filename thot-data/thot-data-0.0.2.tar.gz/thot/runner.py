
# coding: utf-8

# # Runner

# In[1]:


import os
import sys
import subprocess

from pymongo import MongoClient
from bson.objectid import ObjectId

from .db.local import LocalDB
from .db.mongo import MongoDB
from .classes.container import Container


# In[ ]:


def run_script( script_id, script_path, container_id ):
    """
    Runs the given program form the given Container.
    
    :param script_id: ID of the script
    :param script_path: Path to the script..
    :param container: ID of the container to run from.
    """
    # setup environment
    env = os.environ.copy()
    env[ 'THOT_CONTAINER_ID' ] = container_id # set root container to be used by thot library
    env[ 'THOT_SCRIPT_ID' ]    = script_id    # used in project for adding Assets
    
    # TODO [0]: Ensure safely run
    # run program
    subprocess.call(
        'python {}'.format( script_path ),
        shell = True,
        env = env
    )
    
    
def eval_tree( root, db ):
    """
    Runs scripts on the Container tree.
    Uses DFS, running from bottom up.
    
    :param root: Container.
    :param db: Database
    """
    hosted = isinstance( db, MongoDB )
    
    if hosted:
        root = ObjectId( root )
        
    root = db.containers.find_one( { '_id': root } )
    root = Container( **root )
    
    # eval children
    for child in root.children:
        eval_tree( child, db )

    # eval self
    scripts = root.scripts
    scripts.sort()
    for association in scripts:
        if not association.autorun:
            continue

        if hosted:
            script_id = association.script
            
            # get script path
            script = db._scripts.find_one( { 
                '_id': ObjectId( script_id ) 
            } )

            script_path = script[ 'file' ]
            
        else: # local
            # local project script paths are prefixed by path id
            script_id = script_path = os.path.normpath( # path to script
                os.path.join( root._id, association.script )
            )
            
        run_script( str( script_id ), script_path, str( root._id ) ) # convert ids from ObjectId, if necessary


# In[2]:


def run_local( root ):
    """
    Runs programs bottom up for local projects.
    
    :param root: Path to root.
    """
    db = LocalDB( root )
    eval_tree( root, db )
    
    
def run_hosted( user, root ):
    """
    Runs a hosted project.
    
    :param user: ID of user.
    :param root: ID of root Container.
    """
    os.environ[ 'THOT_USER_ID' ] = user
    
    db = MongoDB()
    eval_tree( root, db )


# In[4]:


if __name__ == '__main__':
    """
    Runs a Thot Project from console.
    """
    from argparse import ArgumentParser
    
    parser = ArgumentParser( description = 'Thot project runner for Python.' )
    
    parser.add_argument(
        '-r', '--root',
        type = str,
        default = '.',
        help = 'Path or ID of the root Container.'
    )
    
    parser.add_argument(
        '-env', '--environment',
        type = str,
        choices = [ 'local', 'hosted' ],
        default = 'local',
        help = 'Environment of the runner.'
    )
    
    parser.add_argument(
        '-u', '--user',
        type = str,
        help = 'User ID. Required for hosted environment.'
    )
    
    args = parser.parse_args()

    if args.environment == 'local':
        run_local( os.path.abspath( args.root ) )
        
    elif args.environment == 'hosted':
        if not args.user:
            raise RuntimeError( 'User is required for runner in a hosted environment.' )
        
        run_hosted( args.user, args.root )


# # Work

# In[4]:


# root = os.path.normpath(
#     os.path.join( os.getcwd(), '../_tests/projects/inclined-plane' )
# )

# run_local( root )

