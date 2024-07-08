from backend.scraper.main import do_launch_scraper

if __name__ == '__main__':
    giveaways_traceback_infos, msrp_traceback_infos, steam_grid_db_traceback_infos, database_traceback_infos = do_launch_scraper()
    giveaways_traceback_infos = [
        i for i in giveaways_traceback_infos if i is not None
    ]
    database_traceback_infos = [
        i for i in database_traceback_infos if i is not None
    ]
    if giveaways_traceback_infos:
        print("\n".join(giveaways_traceback_infos))
    if msrp_traceback_infos:
        print(msrp_traceback_infos)
    if steam_grid_db_traceback_infos:
        print(steam_grid_db_traceback_infos)
    if database_traceback_infos:
        print("\n".join(database_traceback_infos))
