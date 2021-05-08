from rest_framework import serializers
from api.models import Coin, Key

class CoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coin
        fields = ('id',
                  'name',
                  'symbol',
                  'open',
                  'high',
                  'low',
                  'close',
                  'volume',
                  'last_update')

class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = ('id',
                  'hash',
                  'expiry_date'
                  )
