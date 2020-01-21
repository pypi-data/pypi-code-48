from scipy.stats import norm
from scipy import optimize, exp, log, sqrt

class BlackScholesEquation():
    """[Black Scholes Equation]
    Refer: 
        1. https://www.monte-carlo-note.com/2017/04/python-option-premium-BS.html
        2. https://www.jpx.co.jp/learning/derivatives/options/02.html
        3. http://delta-hedge.xyz/nky_iv/
    Returns:
        [type] -- [description]
    """

    @classmethod
    def call(cls, S0, sigma ,r, q, T, K):
        """[Call option theoretical price]
        
        Arguments:
            S0 {[type]} -- [当日のオプション生産指数]
            sigma {[type]} -- [JPXが定めるところにより各銘柄ごとに算出する当該オプション対象株価指数の予測変動率]
            r {[type]} -- [全国銀行協会が前日に公表する日本東京銀行間取引金利のうち、当該銘柄の権利行使日までの日数を勘定してJPXが指定する金利]
            q {[type]} -- [当社が指定する予想利回り]
            T {[type]} -- [当日から当該銘柄の権利行使日までの日数/365]
            K {[type]} -- [当該銘柄の権利行使価格]
        
        Returns:
            [type] -- [description]
        """
        d1 = (log(S0 / K) + (r - q) * T) / (sigma * sqrt(T))+sigma*sqrt(T)/ 2
        d2 = (log(S0 / K) + (r - q) * T) / (sigma * sqrt(T))-sigma*sqrt(T)/ 2
        call = S0 * exp(-q * T)* norm.cdf(x=d1, loc=0, scale=1) -K * exp(-r * T) * norm.cdf(x=d2, loc=0, scale=1)
        return call

    @classmethod
    def put(cls, S0, sigma ,r, q, T, K):
        """[Put option]
        
        Arguments:
            S0 {[type]} -- [description]
            sigma {[type]} -- [description]
            r {[type]} -- [description]
            q {[type]} -- [description]
            T {[type]} -- [description]
            K {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        d1 = (log(S0 / K) + (r - q + sigma**2 / 2) * T) / (sigma * sqrt(T))
        d2 = d1 - sigma * sqrt(T)
        put = K * exp(-r * T) * norm.cdf(x=-d2, loc=0, scale=1) -S0 * exp(-q * T) * norm.cdf(x=-d1, loc=0, scale=1)
        return put

    @classmethod
    def put_call_parity(cls, S0, sigma ,r, q, T, K):
        return cls.call(S0, sigma ,r,q,T,K)+K*exp(-r*T) - cls.put(S0, sigma ,r,q,T,K)-S0*exp(-q*T)
    
    @classmethod
    def iv_call(cls, S0, r, q, T, K, option_market_price):
        """[Implied Volatility]
        
        Arguments:
            S0 {[type]} -- [description]
            r {[type]} -- [description]
            q {[type]} -- [description]
            T {[type]} -- [description]
            K {[type]} -- [description]
            option_market_price {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        def _h(sigma):
            h = cls.call(S0, sigma ,r, q, T, K) - option_market_price
            return h
        iv = optimize.fsolve(_h, 0.2) 
        return iv[0]
    
    @classmethod
    def iv_put(cls, S0, r, q, T, K, option_market_price):
        """[Implied Volatility]
        
        Arguments:
            S0 {[type]} -- [description]
            r {[type]} -- [description]
            q {[type]} -- [description]
            T {[type]} -- [description]
            K {[type]} -- [description]
            option_market_price {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        def _h(sigma):
            h = cls.put(S0, sigma ,r, q, T, K) - option_market_price
            return h
        iv = optimize.fsolve(_h, 0.2) 
        return iv[0]