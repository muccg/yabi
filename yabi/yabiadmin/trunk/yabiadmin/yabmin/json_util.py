import datetime

def makeJsonFriendly(data):
  '''Will traverse a dict or list compound data struct and
     make any datetime.datetime fields json friendly
  '''

  try:
      if isinstance(data, list):
          for e in data:
              e = makeJsonFriendly(e)

      elif isinstance(data, dict):
          for key in data.keys():
              data[key] = makeJsonFriendly(data[key])

      elif isinstance(data, datetime.datetime):
          return str(data)

      else:
          pass # do nothing
      
  except Exception, e:
      print 'makeJsonFriendly encountered an error: ', str(e)

  return data
