import pandas as pd
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

import argparse

def elab_champs(df, champ_data):
    df['t1_champ1'] = df['t1_champ1id'].apply(lambda x: champ_data['data'][str(x)]['name'])
    df['t1_champ2'] = df['t1_champ2id'].apply(lambda x: champ_data['data'][str(x)]['name'])
    df['t1_champ3'] = df['t1_champ3id'].apply(lambda x: champ_data['data'][str(x)]['name'])
    df['t1_champ4'] = df['t1_champ4id'].apply(lambda x: champ_data['data'][str(x)]['name'])
    df['t1_champ5'] = df['t1_champ5id'].apply(lambda x: champ_data['data'][str(x)]['name'])
    
    df['t2_champ1'] = df['t2_champ1id'].apply(lambda x: champ_data['data'][str(x)]['name'])
    df['t2_champ2'] = df['t2_champ2id'].apply(lambda x: champ_data['data'][str(x)]['name'])
    df['t2_champ3'] = df['t2_champ3id'].apply(lambda x: champ_data['data'][str(x)]['name'])
    df['t2_champ4'] = df['t2_champ4id'].apply(lambda x: champ_data['data'][str(x)]['name'])
    df['t2_champ5'] = df['t2_champ5id'].apply(lambda x: champ_data['data'][str(x)]['name'])
    
    return df

def clean_df(df, start=True, more=None):
    t1 = ["t1_champ1", "t1_champ2", "t1_champ3", "t1_champ4", "t1_champ5"]
    t2 = ["t2_champ1", "t2_champ2", "t2_champ3", "t2_champ4", "t2_champ5"]
    additional = ["firstBlood", "winner"] if start is not True else ["winner"]
    if more is not None:
        additional = additional + ['firstDragon'] if more >= 1 else additional
        additional = additional + ['firstTower'] if more >= 2 else additional
        additional = additional + ['firstInhibitor'] if more >= 3 else additional
        additional = additional + ['firstBaron'] if more >= 4 else additional
    # additional = additional + ['firstRiftHerald'] if more == 5 else additional

    df = df[t1 + t2 + additional]
    # print(df)

    encodings1 = [pd.get_dummies(df[col], prefix="t1") for col in t1]
    encodings2 = [pd.get_dummies(df[col], prefix="t2") for col in t2]
    
    combined_df1 = sum(encodings1)
    combined_df2 = sum(encodings2)
    
    df =df.join(combined_df1).join(combined_df2)
    df = df.drop(t1 + t2, axis=1)
    # print(df)
    return df


def model(data):
    X_train, X_test, y_train, y_test = data

    clf = RandomForestClassifier(n_jobs=-1)
    clf.fit(X_train, y_train)
    print(clf.score(X_test, y_test))
    
    importances = dict(zip(clf.feature_names_in_, clf.feature_importances_))
    sorted_importances = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    # print(sorted_importances)
    return


def champ_winrate(df, champ_name):
    wins1 = len(df[(df[f't1_{champ_name}'] == 1) & (df['winner'] == 1)])
    wins2 = len(df[(df[f't2_{champ_name}'] == 1) & (df['winner'] == 2)])

    losses1 = len(df[(df[f't1_{champ_name}'] == 1) & (df['winner'] == 2)])
    losses2 = len(df[(df[f't2_{champ_name}'] == 1) & (df['winner'] == 1)])
    
    try:
        winrate = (wins1 + wins2) / (wins1 + wins2 + losses1 + losses2)
    except ZeroDivisionError:
        return None
    
    return winrate


def main():
    
    args = args_parser()
    start = args.start
    more = args.more
    
    df = pd.read_csv('../data/game_emerald.csv')

    # print(df.columns)
    # print(df.seasonId.value_counts())  # season 9???

    champ_data = json.load(open("../data/champion_info_3.json"))
    
    df = elab_champs(df, champ_data)
    # print(df)
    
    df = clean_df(df, start, more)
    
    X, y = df.drop('winner', axis=1), df['winner']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    data = (X_train, X_test, y_train, y_test)
    model(data)
    
    if args.champion is not None:
        champ_name = args.champion
        winrate = champ_winrate(df, champ_name)
        if winrate is not None:
            print(f"Winrate of {champ_name}: {str(winrate)}")
        else:
            print("Error occurred")


def args_parser():
    parser = argparse.ArgumentParser(description='Predict the winner of a League of Legends game')
    parser.add_argument('-s', '--start', action='store_true', help='Start of the game, only uses starting champions')
    parser.add_argument('-m', '--more', type=int, help='More arguments, uses more data (1-5)')
    parser.add_argument('-c', '--champion', type=str, help='Champion name to get winrate')
    return parser.parse_args()


if __name__ == "__main__":
    main()
