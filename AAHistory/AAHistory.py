# -*- coding: utf-8 -*-
"""
@author: mlv
"""

from AAFileSystem import AAFileSystem
from AAModule import AAModule
from pydriller import Repository
from pydriller import ModificationType

repo = Repository(AAFileSystem.get_code_root_folder())
all_commits_generator = repo.traverse_commits()
all_commits = list(all_commits_generator)


def get_all_commits():
    return all_commits

def print_commit_details(commits):
  for commit in commits:
      print(f"--->> {commit.msg}")
      print(commit.author.name)
      print(commit.author_date)
      print(commit.hash )
      print("\n")

      for each in commit.modified_files:
          print(f" {each.change_type.name}")
          print(f" - {each.old_path}")
          print(f" - {each.new_path}")
      
      print("\n\n")

def count_changes(commits):
    
    # a dictionary that is automatically initialized 
    # if key is absent
    from collections import defaultdict
    commit_counts = defaultdict(int)    

    for commit in commits:
        for modification in commit.modified_files:
            
            new_path = modification.new_path
            old_path = modification.old_path
            
            # try:

            if modification.change_type == ModificationType.RENAME:
                commit_counts[new_path]=commit_counts.get(old_path, 0) + 1
                
                try:
                    commit_counts.pop(old_path)
                except Exception as e:
                    # not sure why sometimes there's a rename w/o 
                    # an old_path existing?
                    # print(f"could not pop {old_path}")
                    # print(f"new path: {new_path}")
                    # print(f"commit: {commit.hash} {commit.msg}")
                    pass

            elif modification.change_type == ModificationType.DELETE:
                commit_counts.pop(old_path, '')

            elif modification.change_type == ModificationType.ADD:
                commit_counts[new_path] = 1

            else: 
                # modification to existing file
                commit_counts [old_path] += 1
            
    return sorted(commit_counts.items(), key=lambda x:x[1])

# pretty print the results
def print_commit_counts(commits):
    for file, count in count_changes(commits):
        print(f"{count} {file}")

        
def get_churns(commits):

    from collections import defaultdict
    file_churns = defaultdict(int)    

    for commit in commits:
        for modified_file in commit.modified_files:
            if modified_file.change_type == ModificationType.RENAME:
                # move the churn count to the new file path
                file_churns[modified_file.new_path] = file_churns[modified_file.old_path]
                file_churns.pop(modified_file.old_path)
                continue

            if modified_file.change_type == ModificationType.ADD:
                continue  # don't count the initial lines
            if modified_file.change_type == ModificationType.DELETE:
                if modified_file.old_path in file_churns:
                    file_churns.pop(modified_file.old_path) # no longer interesting.

            if modified_file.change_type == ModificationType.MODIFY:
                churn = modified_file.added_lines + modified_file.deleted_lines
                file_churns[modified_file.new_path] += churn
    return sorted(file_churns.items(), key=lambda x:x[1], reverse=True)

def print_churns(commits):
    for file, churn in get_churns(commits):
        print(f"{churn} {file}")

# print_churns(all_commits)

def add_churns_for_modules(modules):
    file_churns = get_churns(get_all_commits())
    for module in modules:
        module_local_path = module.full_path[len(AAFileSystem.CODE_ROOT_FOLDER):] # remove root part of the path
        if module_local_path in file_churns:
            module.churn = file_churns[module_local_path]
    accumulate_churn(modules)
            
def accumulate_churn(modules):
    for module in modules:
        module_name = module.full_name
        while (pos := module_name.rfind(".")) > 0:
            module_name = module_name[:pos - 1] # find next ancestor
            for module2 in modules:
                if module2.full_name == module_name:
                    # next ancestor found. Add our churn to the ancestor
                    module2.churn += module.churn
                    break
                

