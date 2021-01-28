from flask import Flask
import pandas as pd
from models import scale_and_fit, get_and_scale, polish_main_df, generate_main_dict, polished_df_sortby_mls


#TODO: add f4 probability, etc to team pages
#TODO: add and link writeup 'here'
#TODO: Add 2020 teams

app = Flask(__name__)
pd.set_option('display.max_colwidth', -1)
recdf = pd.read_csv('data/recdf_final.csv', index_col = 0)

mega_df = pd.read_csv("data/mega_df.csv", index_col=0)
scaler, neigh, h = scale_and_fit(mega_df)
df_curr, c = get_and_scale(scaler)

df = polish_main_df(generate_main_dict(df_curr, c, neigh, mega_df).reset_index(drop=True))


main_html_string = '''
<html>
  <head><title>CBBSIM - College Hoops Historical Comparisons</title>
  <link rel="stylesheet" href="static/styles/style.css">
  </head>
  
  <header class="hstyle">
    <h1 style="text-align:center; font-size=10pt"> <a href="/">Current Season</a> | 2020 (Coming Soon) </h1>
    <h2 style="text-align:center; font-size=16pt"> College Basketball Similarity Rankings </h2>
        <p style="text-align:center; font-size=8pt;"> Using historic data from KenPom and BartTorvik, this website finds which past NCAA
         men's basketball teams most nearly match this year's field, and offers statistics based on this info. </p>
        <p style="text-align:center; font-style:italic; font-size=8pt;"> <b>How to use:</b> This page displays at-a-glance info for all teams. Click any individual current or historic
        team for a more complete list of their nearest comparisons. For a more detailed writeup, click 
        <a href="https://www.google.com/">here</a>. </p>
  </header>
  
  <style> 
   table, th, td {{font-size:12pt; text-align:center;}}
   table {{style:center}}
  th, td {{padding: 5px;}}
  td {{font-size:10pt;}}
 
</style>
  <body style="background-color:#f2f8ff;">
    {table}
  </body>
  <footer class="fstyle">
    <p> Designed by Devlin Sullivan | Contact: devlin.s@wustl.edu </p>
  </footer>
</html>.
'''
df1 = polished_df_sortby_mls(df)

@app.route('/')
def table():
    asd = df
    c = 'Avg. Seed'
    ctitle = '<a href="' + c + '">' + c + "</a>"
    asd[ctitle] = [x if x != "None" else 17 for x in asd[ctitle].tolist()]
    asd[ctitle] = asd[ctitle].astype('float')
    asd = asd.sort_values(ctitle, ascending=True)
    asd[ctitle] = [x if x != 17 else "None" for x in asd[ctitle].tolist()]
    mtitle = '<a href="' + 'Most Likely Seed' + '">' + 'Most Likely Seed' + "</a>"
    asd[mtitle] = [x if x not in [0, 17] else "None" for x in asd[mtitle].tolist()]
    asd['Rank'] = range(1, len(df) + 1)
    return main_html_string.format(table=asd.to_html(index=False, classes='mystyle', escape=False))


@app.route('/<school>')
def team(school):
    from models import historical_page, process_seed_dist, list_to_hist
    second_string = ""
    make = -1
    avg_seed = -1
    school_name = ""
    img_string = "<p> <br /> </p>"
    try:
        team_df, team_pred, current = historical_page(school, df_curr, mega_df, neigh, h, c, recdf)
    except KeyError:
        return main_html_string.format(table=df1.to_html(index=False, classes='mystyle', escape=False))
    team_df = team_df.rename(columns={'Label':'Team', 'S':'Seed', 'distance':'Distance'})
    team_df = team_df[['Team', 'Record', 'Distance', 'Seed', 'NCAAT Result']]
    if current:
        proc = process_seed_dist(team_pred['seed_dist'])
        make = str(round(proc[0] * 100, 2)) + "%"
        second_string = "Implied Likelihood of Making Tournament"
        try:
            avg_seed = round(proc[2], 2)
        except TypeError:
            avg_seed = "None"
        school_name = team_pred['team']
        img_string = '<p><img src="data:image/png;base64,{}", alt="Seed Distribution", class="istyle"></p>'.format(list_to_hist(team_pred['seed_dist']))
    else:
        make = int(team_pred[1])
        if make == 17:
            make = 'None'
        second_string = "Actual Seed"
        try:
            avg_seed = round(team_pred[0], 2)
        except TypeError:
            avg_seed = "None"
        school_name = school
    team_html_string = '''
    <html>
      <head><title> CBBSIM - {teamname} Page</title>
      <link rel="stylesheet" href="static/styles/style.css">
      </head>

      <header class="hstyle">
        <h1 style="text-align:center; font-size=10pt"> <a href="/">Home</a> </h1>
        <h2 style="text-align:center; font-size=16pt"> Team Page: {teamname} </h2>
        <h2 style="text-align:center; font-size=14pt">Average Seed from Neighbors: {avg_seed} | {string_two}: {p_make}</h2>
        {image_string}
      </header>
        
        
      <style> 
        table, th, td {{font-size:12pt; text-align:center;}}
        table {{style = "margin-left: 5%; margin-right: a"}}
        th, td {{padding: 5px;}}
        td {{font-size:10pt;}}

    </style>
      <body style="background-color:#f2f8ff;">
        {table}
        
      </body>
     
      <footer class="fstyle">
            <p> Designed by Devlin Sullivan | Contact: devlin.s@wustl.edu </p>
        </footer>
    </html>. 
    '''
    team_df['Team'] = team_df['Team'].apply(lambda x: '<a href="' + x + '">' + x + "</a>")
    team_df['Seed'] = team_df['Seed'].apply(lambda x: int(x) if x != 'None' else x)
    return team_html_string.format(table=team_df.to_html(index=False, classes='mystyle', escape=False),
                                   teamname=school_name, avg_seed=avg_seed, p_make=make, image_string=img_string,
                                   string_two=second_string)

@app.route('/Made Tourney')
def made():
    c = 'Most Likely Seed'
    ctitle = '<a href="' + c + '">' + c + "</a>"
    df2 = df
    df2[ctitle] = [x if x != 0 else "None" for x in df2[ctitle].tolist()]
    mtitle = '<a href="' + 'Most Likely Seed' + '">' + 'Most Likely Seed' + "</a>"
    df2[mtitle] = [x if x != 17 else "None" for x in df2[mtitle].tolist()]
    aaseed = mtitle = '<a href="' + 'Avg. Seed' + '">' + 'Avg. Seed' + "</a>"
    df2[aaseed] = [x if x != 17 else "None" for x in df2[aaseed].tolist()]
    df2['Rank'] = range(1, len(df) + 1)
    return main_html_string.format(table=df2.to_html(index=False, classes='mystyle', escape=False))

@app.route('/Most Likely Seed')
def mode():
    mls = df
    c = 'Most Likely Seed'
    ctitle = '<a href="' + c + '">' + c + "</a>"
    mls[ctitle] = [x if x in range(1,17) else 17 for x in mls[ctitle].tolist()]
    mls = mls.sort_values(ctitle, ascending=True)
    mls[ctitle] = [x if x != 17 else "None" for x in mls[ctitle].tolist()]
    c = 'Avg. Seed'
    ctitle = '<a href="' + c + '">' + c + "</a>"
    mls[ctitle] = [x if x != 17 else "None" for x in mls[ctitle].tolist()]
    mls['Rank'] = range(1,len(df) + 1)
    return main_html_string.format(table=mls.to_html(index=False, classes='mystyle', escape=False))

@app.route('/Avg. Seed')
def avgseed():
    asd = df
    c = 'Avg. Seed'
    ctitle = '<a href="' + c + '">' + c + "</a>"
    asd[ctitle] = [x if x != "None" else 17 for x in asd[ctitle].tolist()]
    asd[ctitle] = asd[ctitle].astype('float')
    asd = asd.sort_values(ctitle, ascending=True)
    asd[ctitle] = [x if x != 17 else "None" for x in asd[ctitle].tolist()]
    mtitle = '<a href="' + 'Most Likely Seed' + '">' + 'Most Likely Seed' + "</a>"
    asd[mtitle] = [x if x not in [0, 17] else "None" for x in asd[mtitle].tolist()]
    asd['Rank'] = range(1, len(df) + 1)
    return main_html_string.format(table=asd.to_html(index=False, classes='mystyle', escape=False))

if __name__ == "__main__":
    app.run(debug=True)
