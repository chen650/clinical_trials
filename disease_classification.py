import pandas as pd
from fuzzyset import FuzzySet
import re

df = pd.read_excel("2018_1Q.xlsx",sheet_name="SearchResults");
icd = pd.read_excel("icd10conversion.xlsx",sheet_name="Sheet1");

# #### test the above with smaller amt of data for speed
# df = df[0:9]
# ####

# fuzzy match trial conditions to ICD descriptions
conds = df['Conditions'];
corpus = list(icd['Description']);
codes = icd['Code'];
categories = icd['Category'];
fs = FuzzySet(corpus);
res = list();
acc = list();
healthyMatch = re.compile("Healthy");
for val in conds:
  if pd.isnull(val):
    resArr = '';
    accArr = 0;
  else:
    condArr = val.split("|"); # there can be multiple conditions in a trial
    resArr = list();
    accArr = list();
    for c in condArr:
      if healthyMatch.match(c): # if term indicates healthy patient
        resArr.append('');
        accArr.append(0);
      else:
        term = c;
        term = re.sub('Cancer','Neoplasm', c);
        match = fs.get(term)[0];
        resArr.append(match[1]);
        accArr.append(match[0]);
  res.append(resArr);
  acc.append(accArr);

# translate ICD descriptions to corresponding second-level ICD category
catList = list(); 
for resVal in res: # each trial
  if resVal == '':
    catStr = "";
  else:
    catStr = "";
    for descr in resVal: # each translated condition within a trial
      cat = "";
      for i, r in enumerate(corpus): # check each row in icd corpus
        if(descr == r): # if the translated condition is of this row in icd corpus, find category
          cat = categories[i];
          catStr = "|".join([catStr,cat]);
          break;
  catList.append(catStr);

# add column of chapters to trials dataframe
catList = pd.Series(catList);
df['ICD10_Categories'] = catList.values;

acc = pd.Series(acc);
df['ICD10_Accuracy'] = acc.values;

# write trial data with column of chapters to csv
df.to_excel('trials_classified2018_0223.xlsx');
