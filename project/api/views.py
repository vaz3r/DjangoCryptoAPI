from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.utils.timezone import now

from .models import Coin, Key
from .serializers import CoinSerializer
from rest_framework.decorators import api_view
import requests
import environ
env = environ.Env()
environ.Env.read_env('./backend/.env')

# Functions ========================================>

def FetchAlphavantage():
    try:
        URL = 'https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol=BTC&market=USD&interval=1min&apikey={}'.format(
            env('ALPHAVANTAGE_API_KEY'))

        headers = {
            'authority': 'www.alphavantage.co',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9,fr;q=0.8,pt;q=0.7,ar;q=0.6'
        }

        response = requests.request('GET', URL, headers=headers)

        return response.json()
    except Exception as error:
        print(error)

# Views ============================================>

@api_view(['GET', 'POST'])
def coin_info(request):
    Force = False
    apiKey = request.GET['apiKey']

    if (request.method == 'POST'):
        Force = True

    if (apiKey != None and len(apiKey) > 10):
        try:
            # Authentication based on api key ========================================>
            Authorization = Key.objects.filter(
                hash=apiKey,
                expiry_date__gt=now()
            )

            if (len(Authorization) > 0):
                try:
                    CoinDetails = Coin.objects.filter(
                        symbol='BTC'
                    )

                    if (len(CoinDetails) > 0):
                        # Checking data freshness ========================================>
                        if (CoinDetails[0].LastRefresh > 60 or Force == True):
                            # Data is stale => Refetch ========================================>
                            CoinID = CoinDetails[0].id

                            # Alphavantage has a very badly desiged API
                            # So we have to deal with the bad design by iterating through the data by indexes
                            
                            DataPipe = FetchAlphavantage()
                            UpdateTime = now()

                            DataPipe = list(DataPipe.items())
                            Metadata = list(DataPipe[0][1].items())
                            Timeseries = list(DataPipe[1][1].items())
                            Timeseries = list(Timeseries[0][1].items())

                            Symbol = Metadata[1][1]
                            Name = Metadata[2][1]
                            Open = Timeseries[0][1]
                            High = Timeseries[1][1]
                            Low = Timeseries[2][1]
                            Close = Timeseries[3][1]
                            Volume = Timeseries[4][1]

                            # Doing an upsert and making sure the last_update is updated
                            # So we can re-evaluate the cache again

                            if CoinDetails[0].LastRefresh > 60:
                                Coin.objects.update_or_create(id=CoinID, defaults={
                                    'name': Name,
                                    'symbol': Symbol,
                                    'open': Open,
                                    'high': High,
                                    'low': Low,
                                    'close': Close,
                                    'volume': Volume,
                                    'last_update': UpdateTime,
                                })

                            return JsonResponse(
                                {
                                    'id': CoinID,
                                    'name': Name,
                                    'symbol': Symbol,
                                    'open': Open,
                                    'high': High,
                                    'low': Low,
                                    'close': Close,
                                    'volume': Volume,
                                    'last_update': UpdateTime
                                }
                            )
                        else:
                            # Data is new => Serve ========================================>
                            return JsonResponse(CoinSerializer(CoinDetails[0]).data)
                    else:
                        return JsonResponse({'message': 'Coin does not exist'}, status=status.HTTP_404_NOT_FOUND)

                except Coin.DoesNotExist:
                    return JsonResponse({'message': 'Coin does not exist'}, status=status.HTTP_404_NOT_FOUND)

            else:
                return JsonResponse({'message': 'Not authorized to access this resource.'}, status=status.HTTP_401_UNAUTHORIZED)

        except Key.DoesNotExist:
            return JsonResponse({'message': 'Not authorized to access this resource.'}, status=status.HTTP_401_UNAUTHORIZED)

    else:
        return JsonResponse({'message': 'Please specify a valid api key.'}, status=status.HTTP_401_UNAUTHORIZED)