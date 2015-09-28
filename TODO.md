
1. Create simple database to store job site information (ie z coordinates to levels)
2. Store XML files in database instead of outside dependence on S3
3. Remove all outside dependencies, mainly S3
4. Remove caching layer that's only there to stop S3 call
5. Dockerize application so that others can easily use it
6. Basic front end improvements, like viewing job site information
7. View the clashes in a 2D view per level, the radius of the dot indicating number of clashes
8. Same as 2D but in 3D
9. Work on ranking system to allow for quick triage (ie "move this one pipe and clear up 10 clashes")
