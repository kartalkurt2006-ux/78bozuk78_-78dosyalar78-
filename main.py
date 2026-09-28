from datetime import datetime
import json
import os
import time
import numpy as np
import pandas as pd
import pytz
import requests
import yfinance as yf

# --- AYARLAR VE SABİTLER ---
COOLDOWN_SECONDS = 3600  # Aynı hisse ve aynı periyot için 1 saat bekleme süresi
TZ_TR = pytz.timezone("Europe/Istanbul")

# Ntfy Kanal Ayarı
NTFY_URL = "https://ntfy.sh/borsa_senet"

# Tek Merkezi Hafıza Dosyası
MERKEZI_HAFIZA_DOSYASI = "borsa_hafiza.json"

# BIST Tüm Hisseler (MARKA.IS çıkarıldı)
STOCKS = [
    "AAVST.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS", "ADGYO.IS", "AEFES.IS", "AFYON.IS", "AGESA.IS", "AGHOL.IS", "AGROT.IS",
    "AKBNK.IS", "AKENR.IS", "AKFGY.IS", "AKFYE.IS", "AKGRT.IS", "AKMGY.IS", "AKSA.IS", "AKSEN.IS", "AKSGY.IS", "ALARK.IS",
    "ALBRK.IS", "ALCAR.IS", "ALCTL.IS", "ALFAS.IS", "ALKA.IS", "ALKIM.IS", "ALKLC.IS", "ALMAT.IS", "ANELE.IS", "ANGEN.IS",
    "ANHYT.IS", "ANSGR.IS", "ARASE.IS", "ARCLK.IS", "ARDYZ.IS", "ARENA.IS", "ARSAN.IS", "ARTMS.IS", "ARZUM.IS", "ASELS.IS",
    "ASTOR.IS", "ASUZU.IS", "ATAKP.IS", "ATATP.IS", "ATEKS.IS", "ATLAS.IS", "AVGYO.IS", "AVOD.IS", "AVPGY.IS", "AYCES.IS",
    "AYDEM.IS", "AYEN.IS", "AYES.IS", "AYGAZ.IS", "AZTEK.IS", "BAGFS.IS", "BAKAB.IS", "BALAT.IS", "BANVT.IS", "BARMA.IS",
    "BASCM.IS", "BASGZ.IS", "BAYRK.IS", "BEGYO.IS", "BERA.IS", "BEYAZ.IS", "BIENY.IS", "BIGCH.IS", "BIMAS.IS", "BINHO.IS",
    "BIOEN.IS", "BIZIM.IS", "BJKAS.IS", "BLCYT.IS", "BMSCH.IS", "BMSTL.IS", "BNTAS.IS", "BOBET.IS", "BORLS.IS", "BOSSA.IS",
    "BRISA.IS", "BRKO.IS", "BRKSN.IS", "BRLSM.IS", "BRMEN.IS", "BRYAT.IS", "BSOKE.IS", "BTCIM.IS", "BUCIM.IS", "BURCE.IS",
    "BURVA.IS", "BVSAN.IS", "BYDNR.IS", "CANTE.IS", "CASFY.IS", "CCOLA.IS", "CELHA.IS", "CEMAS.IS", "CEMTS.IS", "CEOEM.IS",
    "CGCAM.IS", "CIMSA.IS", "CLEBI.IS", "CMBTN.IS", "CMENT.IS", "CONSE.IS", "COSMO.IS", "CRDFA.IS", "CRFSA.IS", "CUSAN.IS",
    "CVKMD.IS", "CWENE.IS", "DAGI.IS", "DAPGM.IS", "DARDL.IS", "DENGE.IS", "DERHL.IS", "DERIM.IS", "DESA.IS", "DESPC.IS",
    "DEVA.IS", "DIRIT.IS", "DITAS.IS", "DMRGD.IS", "DMSAS.IS", "DNISI.IS", "DOAS.IS", "DOBUR.IS", "DOCO.IS", "DOGUB.IS",
    "DOHOL.IS", "DSTAN.IS", "DUNYA.IS", "DURDO.IS", "DYOBY.IS", "DZGYO.IS", "EBEBK.IS", "ECILC.IS", "ECZYT.IS", "EDIP.IS",
    "EGEEN.IS", "EGEPO.IS", "EGGUB.IS", "EGPRO.IS", "EGSER.IS", "EKGYO.IS", "EKOS.IS", "EKSUN.IS", "ELITE.IS", "EMKEL.IS",
    "ENERY.IS", "ENKAI.IS", "ENJSA.IS", "EPLAS.IS", "ERBOS.IS", "EREGL.IS", "ERSU.IS", "ESCAR.IS", "ESCOM.IS", "ESEN.IS",
    "ETILR.IS", "EUHOL.IS", "EUKYO.IS", "EUPWR.IS", "EUREN.IS", "EUYO.IS", "EYGYO.IS", "FADE.IS", "FENER.IS", "FLAP.IS",
    "FMIZP.IS", "FONET.IS", "FORMT.IS", "FRIGO.IS", "FROTO.IS", "GARAN.IS", "GARFA.IS", "GEDIK.IS", "GEDZA.IS", "GENIL.IS",
    "GENTS.IS", "GEREL.IS", "GESAN.IS", "GLBMD.IS", "GLCVY.IS", "GLRYH.IS", "GLYHO.IS", "GMTAS.IS", "GOKNR.IS", "GOLTS.IS",
    "GOODY.IS", "GOZDE.IS", "GRNYO.IS", "GRSEL.IS", "GTRGY.IS", "GUBRF.IS", "GWIND.IS", "GZNMI.IS", "HALKB.IS", "HATEK.IS",
    "HATSN.IS", "HEDEF.IS", "HEKTS.IS", "HKTM.IS", "HLGYO.IS", "HTTBT.IS", "HUBVC.IS", "HURGZ.IS", "ICBCT.IS", "IDEAS.IS",
    "IDGYO.IS", "IENTS.IS", "IHEVA.IS", "IHGZT.IS", "IHLAS.IS", "IHLGM.IS", "IMASM.IS", "INDES.IS", "INFO.IS", "INGRM.IS",
    "INTEM.IS", "INVEO.IS", "INVES.IS", "IPEKE.IS", "ISATR.IS", "ISBIR.IS", "ISBTR.IS", "ISCEN.IS", "ISCTR.IS", "ISFIN.IS",
    "ISGSY.IS", "ISGYO.IS", "ISKPL.IS", "ISKUR.IS", "ISMEN.IS", "ISSEN.IS", "IZENR.IS", "IZFAS.IS", "IZINV.IS", "JANTS.IS",
    "KAPLM.IS", "KAREL.IS", "KARSN.IS", "KARTN.IS", "KARYE.IS", "KATMR.IS", "KAYSE.IS", "KBORU.IS", "KCAER.IS", "KCHOL.IS",
    "KENT.IS", "KERVT.IS", "KFEIN.IS", "KGYO.IS", "KIMMR.IS", "KLGYO.IS", "KLKIM.IS", "KLRHO.IS", "KLMSN.IS", "KLSER.IS",
    "KLSYN.IS", "KMPUR.IS", "KNFRT.IS", "KONTR.IS", "KONYA.IS", "KOPOL.IS", "KORDS.IS", "KOTON.IS", "KOZAA.IS", "KOZAL.IS",
    "KRDMD.IS", "KRGYO.IS", "KRONT.IS", "KRPLS.IS", "KRSTL.IS", "KRTEK.IS", "KZBGY.IS", "KZYGZ.IS", "LIDER.IS", "LIDFA.IS",
    "LKMNH.IS", "LMKDC.IS", "LOGO.IS", "LUKSK.IS", "MAALT.IS", "MAKIM.IS", "MAKTK.IS", "MANAS.IS", "MARTI.IS",
    "MAVI.IS", "MEDTR.IS", "MEGAP.IS", "MEKAG.IS", "MEPET.IS", "MERCN.IS", "MERKO.IS", "METUR.IS", "MGROS.IS", "MIATK.IS",
    "MMCAS.IS", "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MPARK.IS", "MRGYO.IS", "MTRKS.IS", "MTRYO.IS", "MZHLD.IS", "NATEN.IS",
    "NETAS.IS", "NIBAS.IS", "NTHOL.IS", "NUGYO.IS", "NUHCM.IS", "OBAMS.IS", "OBASE.IS", "ODAS.IS", "OFSYM.IS", "ONCSM.IS",
    "ORCAY.IS", "OYYAT.IS", "OZAKD.IS", "OZGYO.IS", "OZKGY.IS", "OZLTM.IS", "OZRDN.IS", "PAKRD.IS", "PAMEL.IS", "PAPIL.IS",
    "PARSN.IS", "PASEU.IS", "PCILT.IS", "PEKGY.IS", "PENGD.IS", "PENTA.IS", "PETKM.IS", "PETUN.IS", "PGSUS.IS", "PINSU.IS",
    "PKART.IS", "PKENT.IS", "PNSUT.IS", "POLHO.IS", "POLTK.IS", "PRDGS.IS", "PRKME.IS", "PRKAB.IS", "PSGYO.IS", "QNBFB.IS",
    "QNBFL.IS", "QUAGR.IS", "RALYH.IS", "REEDR.IS", "RNPOL.IS", "RODRG.IS", "ROYAL.IS", "RTALB.IS", "RUBNS.IS", "RYGYO.IS",
    "RYSAS.IS", "SAFKR.IS", "SAHOL.IS", "SASA.IS", "SAYAS.IS", "SDTTR.IS", "SEGFO.IS", "SEGYO.IS", "SEKFK.IS", "SEKUR.IS",
    "SELEC.IS", "SELVA.IS", "SEYKM.IS", "SILVR.IS", "SISE.IS", "SKBNK.IS", "SKTAS.IS", "SMART.IS", "SMRTG.IS", "SNGYO.IS",
    "SNICA.IS", "SNPAM.IS", "SODSN.IS", "SOKM.IS", "SONME.IS", "SRVGY.IS", "SUMAS.IS", "SUNTK.IS", "SUWEN.IS", "TABGD.IS",
    "TARKM.IS", "TATEN.IS", "TATGD.IS", "TAVHL.IS", "TBORG.IS", "TCELL.IS", "TCKRC.IS", "TDGYO.IS", "TEKTU.IS", "TETMT.IS",
    "TEZOL.IS", "TGSAS.IS", "THYAO.IS", "TKFEN.IS", "TKNSA.IS", "TMPOL.IS", "TMSN.IS", "TOASO.IS", "TRCAS.IS", "TRGYO.IS",
    "TRMET.IS", "TSKB.IS", "TSPOR.IS", "TTKOM.IS", "TTRAK.IS", "TUCLK.IS", "TUPRS.IS", "TURSG.IS", "UFUK.IS", "ULAS.IS",
    "ULUFA.IS", "ULKER.IS", "ULUUN.IS", "VAKBN.IS", "VAKFN.IS", "VAKGY.IS", "VBTYZ.IS", "VERTU.IS", "VERUS.IS", "VESBE.IS",
    "VESTL.IS", "VKFYO.IS", "VKGYO.IS", "VKING.IS", "YAPRK.IS", "YATAS.IS", "YAYLA.IS", "YBTAS.IS", "YEOTK.IS", "YESIL.IS",
    "YGGYO.IS", "YIGIT.IS", "YKBNK.IS", "YKSL.IS", "YUNSA.IS", "YYAPI.IS", "ZEDUR.IS", "ZOREN.IS", "ZRGYO.IS",
]


def calculate_hma(series, period=20):
  half_per = period // 2
  sqrt_per = int(np.sqrt(period))

  def wma(s, p):
    weights = np.arange(1, p + 1)
    return s.rolling(p).apply(
        lambda x: np.dot(x, weights) / weights.sum(), raw=True
    )

  wma_half = wma(series, half_per)
  wma_full = wma(series, period)
  raw_hma = 2 * wma_half - wma_full
  hma = wma(raw_hma, sqrt_per)
  return hma


def calculate_strend(df, period=10, multiplier=3):
  hl2 = (df["High"] + df["Low"]) / 2
  tr = pd.concat([
      df["High"] - df["Low"],
      (df["High"] - df["Close"].shift()).abs(),
      (df["Low"] - df["Close"].shift()).abs()
  ], axis=1).max(axis=1)
  atr = tr.rolling(period).mean()
  lowerband = hl2 - (multiplier * atr)
  return lowerband


def calculate_fisher(df, length=9):
  high = df["High"]
  low = df["Low"]
  close = df["Close"]

  min_low = low.rolling(length).min()
  max_high = high.rolling(length).max()

  price_range = max_high - min_low
  price_range = price_range.replace(0, 1e-10)
  
  price_vals = ((2.0 * (close - min_low) / price_range) - 1.0).values
  val_arr = np.zeros_like(price_vals)
  fish_arr = np.zeros_like(price_vals)
  
  for i in range(len(price_vals)):
    if i == 0:
      val_arr[i] = 0.33 * price_vals[i]
      fish_arr[i] = 0.5 * np.log((1.0 + val_arr[i]) / (1.0 - val_arr[i] + 1e-10))
    else:
      clamped_p = np.clip(price_vals[i], -0.999, 0.999)
      val_arr[i] = 0.33 * clamped_p + 0.67 * val_arr[i-1]
      val_arr[i] = np.clip(val_arr[i], -0.999, 0.999)
      
      fish_val = 0.5 * np.log((1.0 + val_arr[i]) / (1.0 - val_arr[i] + 1e-10))
      fish_arr[i] = 0.5 * fish_val + 0.5 * fish_arr[i-1]

  fish = pd.Series(fish_arr, index=close.index)
  trigger = fish.shift(1).fillna(0)
  return fish, trigger


def check_wave_margins(df, lookback=3):
  try:
    close = df["Close"].values
    high = df["High"].values
    low = df["Low"].values

    if len(close) < 35:
      return False

    wave_sequence = [4, 8, 5, 8, 9]
    total_cycle = sum(wave_sequence)

    recent_high = np.max(high[-total_cycle:])
    recent_low = np.min(low[-total_cycle:])
    margin_range = recent_high - recent_low

    if margin_range == 0:
      return False

    upper_margin_threshold = recent_low + (margin_range * 0.80)

    for i in range(-lookback, 0):
      prev_p = close[i - 1]
      curr_p = close[i]
      if prev_p <= upper_margin_threshold and curr_p > upper_margin_threshold:
        return True

    return False
  except Exception:
    return False


def check_1h_super_breakout_prep(df, lookback=3):
  try:
    close = df["Close"].values
    high = df["High"].values
    low = df["Low"].values

    if len(close) < 35:
      return False

    wave_sequence = [4, 8, 5, 8, 9]
    total_cycle = sum(wave_sequence)

    recent_high = np.max(high[-total_cycle:])
    recent_low = np.min(low[-total_cycle:])
    margin_range = recent_high - recent_low

    if margin_range == 0:
      return False

    upper_margin_threshold = recent_low + (margin_range * 0.80)
    margin_tolerance = upper_margin_threshold * 0.99

    curr_p = close[-1]
    if curr_p >= margin_tolerance:
      return True

    return False
  except Exception:
    return False


def hafiza_yukle():
  if os.path.exists(MERKEZI_HAFIZA_DOSYASI):
    try:
      with open(MERKEZI_HAFIZA_DOSYASI, "r") as f:
        return json.load(f)
    except:
      return {}
  return {}


def hafiza_kaydet(hafiza):
  with open(MERKEZI_HAFIZA_DOSYASI, "w") as f:
    json.dump(hafiza, f, indent=4)


def piyasa_zaman_kontrolu():
  if os.environ.get("FORCE_RUN", "true").lower() == "true":
    return True

  simdi = datetime.now(TZ_TR)
  if simdi.weekday() >= 5:
    return False

  baslangic = simdi.replace(hour=9, minute=30, second=0, microsecond=0)
  bitis = simdi.replace(hour=18, minute=10, second=0, microsecond=0)

  if baslangic <= simdi <= bitis:
    return True
  return False


def send_ntfy(message, baslik):
  try:
    safe_baslik = baslik.encode("ascii", "ignore").decode("ascii")
    headers = {"Title": safe_baslik, "Priority": "high"}
    res = requests.post(
        NTFY_URL, data=message.encode("utf-8"), headers=headers, timeout=10
    )
    print(f"Ntfy Yanıtı ({safe_baslik}): {res.status_code}")
  except Exception as e:
    print(f"Ntfy Mesaj Hatası: {e}")


def run_scanner():
  if not piyasa_zaman_kontrolu():
    print("Borsa seans saatleri dışındayız veya hafta sonu. Tarama atlanıyor.")
    return

  simdi_epoch = time.time()
  print(
      f"[{datetime.now(TZ_TR).strftime('%Y-%m-%d %H:%M:%S')}] 40'ar Hisselik Gruplar (Chunks) ile"
      " Merkezi Tarama Başlatılıyor..."
  )

  tum_hafiza = hafiza_yukle()
  toplanan_sinyaller = []

  # --- 40'ARLI GRUPLARA BÖLEREK TOPLU VERİ ÇEKME ---
  chunk_size = 40
  stock_chunks = [STOCKS[i:i + chunk_size] for i in range(0, len(STOCKS), chunk_size)]

  for chunk_idx, chunk in enumerate(stock_chunks, 1):
    print(f"Grup {chunk_idx}/{len(stock_chunks)} indiriliyor ({len(chunk)} hisse)...")
    
    try:
      df_15m_all = yf.download(chunk, period="1mo", interval="15m", group_by='ticker', progress=False)
      time.sleep(0.5)
      df_1h_all = yf.download(chunk, period="1mo", interval="1h", group_by='ticker', progress=False)
      time.sleep(0.5)
    except Exception as e:
      print(f"Grup {chunk_idx} indirilirken hata oluştu: {e}")
      continue

    for clean_ticker in chunk:
      temiz_isim = clean_ticker.replace(".IS", "")

      tetiklenen_str = []
      guncel_fiyat = 0.0
      toplam_puan = 0.0

      try:
        # İlgili hissenin verisini ayıkla
        df_15m = pd.DataFrame()
        df_1h = pd.DataFrame()

        try:
          if isinstance(df_15m_all.columns, pd.MultiIndex) and clean_ticker in df_15m_all.columns.levels[0]:
            df_15m = df_15m_all[clean_ticker].dropna(how="all")
          elif len(chunk) == 1:
            df_15m = df_15m_all.copy()
        except:
          pass

        try:
          if isinstance(df_1h_all.columns, pd.MultiIndex) and clean_ticker in df_1h_all.columns.levels[0]:
            df_1h = df_1h_all[clean_ticker].dropna(how="all")
          elif len(chunk) == 1:
            df_1h = df_1h_all.copy()
        except:
          pass

        # --- 15 DAKİKALIK STRATEJİLER KONTROLÜ ---
        if not df_15m.empty and len(df_15m) >= 40:
          if isinstance(df_15m.columns, pd.MultiIndex):
            df_15m.columns = df_15m.columns.get_level_values(0)

          close_15 = df_15m["Close"]
          high_15 = df_15m["High"]
          low_15 = df_15m["Low"]
          volume_15 = df_15m["Volume"]
          close_curr_15 = close_15.iloc[-1]
          guncel_fiyat = close_curr_15

          delta_15 = close_15.diff()
          gain_15 = (delta_15.where(delta_15 > 0, 0)).rolling(14).mean()
          loss_15 = (-delta_15.where(delta_15 < 0, 0)).rolling(14).mean()
          rs_15 = gain_15 / (loss_15 + 1e-10)
          rsi_15 = 100 - (100 / (1 + rs_15))
          rsi_curr_15 = rsi_15.iloc[-1]

          tp_15 = (high_15 + low_15 + close_15) / 3
          mf_15 = tp_15 * volume_15
          pos_flow_15 = mf_15.where(tp_15 > tp_15.shift(1), 0).rolling(14).sum()
          neg_flow_15 = mf_15.where(tp_15 < tp_15.shift(1), 0).rolling(14).sum()
          mfi_15 = 100 - (100 / (1 + (pos_flow_15 / (neg_flow_15 + 1e-10))))
          mfi_curr_15 = mfi_15.iloc[-1]

          mf_mult_15 = ((close_15 - low_15) - (high_15 - close_15)) / ((high_15 - low_15) + 1e-10)
          cmf_15 = (mf_mult_15 * volume_15).rolling(20).sum() / (volume_15.rolling(20).sum() + 1e-10)
          cmf_curr_15 = cmf_15.iloc[-1]

          up_move_15 = high_15.diff()
          down_move_15 = -low_15.diff()
          plus_dm_15 = up_move_15.where((up_move_15 > down_move_15) & (up_move_15 > 0), 0)
          minus_dm_15 = down_move_15.where((down_move_15 > up_move_15) & (down_move_15 > 0), 0)
          tr_15 = pd.concat([high_15 - low_15, (high_15 - close_15.shift()).abs(), (low_15 - close_15.shift()).abs()], axis=1).max(axis=1)
          tr_smooth_15 = tr_15.rolling(14).sum()
          plus_di_15 = 100 * (plus_dm_15.rolling(14).sum() / (tr_smooth_15 + 1e-10))
          minus_di_15 = 100 * (minus_dm_15.rolling(14).sum() / (tr_smooth_15 + 1e-10))
          plus_di_curr_15 = plus_di_15.iloc[-1]
          minus_di_curr_15 = minus_di_15.iloc[-1]

          rvol_15 = volume_15 / volume_15.rolling(20).mean()
          rvol_curr_15 = rvol_15.iloc[-1]
          hma20_15 = calculate_hma(close_15, 20)

          # 1. 15m Klasik (Orijinal Bar Kapanışlı Yapı - Koru)
          kural_tipi = "15m_klasik"
          label = "bomba 15"
          if kural_tipi not in tum_hafiza: tum_hafiza[kural_tipi] = {}
          
          bar_sayisi = 6
          recent_df = df_15m.iloc[-(bar_sayisi + 1) : -1]
          pivot = (recent_df["High"].mean() + recent_df["Low"].mean() + recent_df["Close"].mean()) / 3
          birinci_dalga_marji = pivot * 1.0023
          bb_middle = close_15.rolling(20).mean().iloc[-1]
          kapanis_teyit = (close_15.iloc[-2] <= birinci_dalga_marji) and (close_curr_15 > birinci_dalga_marji)

          if kapanis_teyit and (close_curr_15 > bb_middle) and (mfi_curr_15 > 60) and (cmf_curr_15 > -0.20) and (rsi_curr_15 > 50) and (rvol_curr_15 > 0.6):
            if simdi_epoch - tum_hafiza[kural_tipi].get(clean_ticker, 0) > COOLDOWN_SECONDS:
              tetiklenen_str.append(f"• 🔴 {label} (MFi:{mfi_curr_15:.1f}|RSI:{rsi_curr_15:.1f})")
              toplam_puan += 35.0
              tum_hafiza[kural_tipi][clean_ticker] = simdi_epoch

          # 2. 15dk Yakala
          kural_tipi = "15m_profesjonel"
          label = "15dk Yakala"
          if kural_tipi not in tum_hafiza: tum_hafiza[kural_tipi] = {}
          
          sart_wave = check_wave_margins(df_15m, lookback=5)
          if sart_wave and (volume_15.iloc[-1] > volume_15.iloc[-2]) and (rvol_curr_15 > 1.0) and (close_curr_15 > hma20_15.iloc[-1]) and (close_curr_15 >= close_15.rolling(20).mean().iloc[-1]) and (mfi_curr_15 > 25) and (plus_di_curr_15 > 15) and (rsi_curr_15 > 45):
            if simdi_epoch - tum_hafiza[kural_tipi].get(clean_ticker, 0) > COOLDOWN_SECONDS:
              tetiklenen_str.append(f"• 🟢 {label} (MFi:{mfi_curr_15:.1f}|RSI:{rsi_curr_15:.1f})")
              toplam_puan += 30.0
              tum_hafiza[kural_tipi][clean_ticker] = simdi_epoch

          # 3. Yeni acil 15 (Canlı Fiyat Entegrasyonu)
          kural_tipi = "yeni_acil"
          label = "Yeni acil 15"
          if kural_tipi not in tum_hafiza: tum_hafiza[kural_tipi] = {}
          
          if (rvol_curr_15 >= 0.6) and (close_curr_15 > hma20_15.iloc[-1]) and (mfi_curr_15 > 60) and (rsi_curr_15 > 45):
            if simdi_epoch - tum_hafiza[kural_tipi].get(clean_ticker, 0) > COOLDOWN_SECONDS:
              tetiklenen_str.append(f"• 🟡 {label} (MFi:{mfi_curr_15:.1f}|RSI:{rsi_curr_15:.1f})")
              toplam_puan += 20.0
              tum_hafiza[kural_tipi][clean_ticker] = simdi_epoch

          # 4. Süper Fisher 15
          kural_tipi = "super_fisher_15"
          label = "Super Fisher 15"
          if kural_tipi not in tum_hafiza: tum_hafiza[kural_tipi] = {}
          
          strend_line = calculate_strend(df_15m, period=10, multiplier=3)
          fish, trg = calculate_fisher(df_15m, length=9)
          fish_curr, trg_curr = fish.iloc[-1], trg.iloc[-1]
          fish_prev, trg_prev = fish.iloc[-2], trg.iloc[-2]
          sart_fisher = (fish_curr > trg_curr) or ((fish_prev <= trg_prev) and (fish_curr > trg_curr))

          if (rvol_curr_15 >= 0.6) and (close_curr_15 > strend_line.iloc[-1]) and (close_curr_15 > hma20_15.iloc[-1]) and sart_fisher and (mfi_curr_15 > 45) and (plus_di_curr_15 > minus_di_curr_15):
            if simdi_epoch - tum_hafiza[kural_tipi].get(clean_ticker, 0) > COOLDOWN_SECONDS:
              tetiklenen_str.append(f"• 🔵 {label} (MFi:{mfi_curr_15:.1f}|RSI:{rsi_curr_15:.1f})")
              toplam_puan += 25.0
              tum_hafiza[kural_tipi][clean_ticker] = simdi_epoch

        # --- 1 SAATLİK STRATEJİLER KONTROLÜ ---
        if not df_1h.empty and len(df_1h) >= 40:
          if isinstance(df_1h.columns, pd.MultiIndex):
            df_1h.columns = df_1h.columns.get_level_values(0)

          close_1h = df_1h["Close"]
          high_1h = df_1h["High"]
          low_1h = df_1h["Low"]
          volume_1h = df_1h["Volume"]
          close_curr_1h = close_1h.iloc[-1]
          if guncel_fiyat == 0.0:
            guncel_fiyat = close_curr_1h

          delta_1h = close_1h.diff()
          gain_1h = (delta_1h.where(delta_1h > 0, 0)).rolling(14).mean()
          loss_1h = (-delta_1h.where(delta_1h < 0, 0)).rolling(14).mean()
          rs_1h = gain_1h / (loss_1h + 1e-10)
          rsi_1h = 100 - (100 / (1 + rs_1h))
          rsi_curr_1h = rsi_1h.iloc[-1]

          up_move_1h = high_1h.diff()
          down_move_1h = -low_1h.diff()
          plus_dm_1h = up_move_1h.where((up_move_1h > down_move_1h) & (up_move_1h > 0), 0)
          tr_1h = pd.concat([high_1h - low_1h, (high_1h - close_1h.shift()).abs(), (low_1h - close_1h.shift()).abs()], axis=1).max(axis=1)
          plus_di_1h = 100 * (plus_dm_1h.rolling(14).sum() / (tr_1h.rolling(14).sum() + 1e-10))
          plus_di_curr_1h = plus_di_1h.iloc[-1]

          hma20_1h = calculate_hma(close_1h, 20)
          wave_breakout_1h = check_wave_margins(df_1h, lookback=3)

          # 5. 1 Saat Yakala
          kural_tipi = "1h_dalga_gorsel"
          label = "1 Saat Yakala"
          if kural_tipi not in tum_hafiza: tum_hafiza[kural_tipi] = {}

          if (close_curr_1h > hma20_1h.iloc[-1]) and (rsi_curr_1h > 50) and (plus_di_curr_1h > 25) and wave_breakout_1h:
            if simdi_epoch - tum_hafiza[kural_tipi].get(clean_ticker, 0) > COOLDOWN_SECONDS:
              tetiklenen_str.append(f"• 🟣 {label} (RSI:{rsi_curr_1h:.1f}|+DI:{plus_di_curr_1h:.1f})")
              toplam_puan += 25.0
              tum_hafiza[kural_tipi][clean_ticker] = simdi_epoch

          # 6. 1 saat süper
          kural_tipi = "1_saat_super"
          label = "1Saat Super Trend"
          if kural_tipi not in tum_hafiza: tum_hafiza[kural_tipi] = {}

          tp_1h = (high_1h + low_1h + close_1h) / 3
          mf_1h = tp_1h * volume_1h
          pos_flow_1h = mf_1h.where(tp_1h > tp_1h.shift(1), 0).rolling(14).sum()
          neg_flow_1h = mf_1h.where(tp_1h < tp_1h.shift(1), 0).rolling(14).sum()
          mfi_1h = 100 - (100 / (1 + (pos_flow_1h / (neg_flow_1h + 1e-10))))
          mfi_curr_1h = mfi_1h.iloc[-1]

          mf_mult_1h = ((close_1h - low_1h) - (high_1h - close_1h)) / ((high_1h - low_1h) + 1e-10)
          cmf_1h = (mf_mult_1h * volume_1h).rolling(20).sum() / (volume_1h.rolling(20).sum() + 1e-10)
          cmf_curr_1h = cmf_1h.iloc[-1]

          sart_1h_super_prep = check_1h_super_breakout_prep(df_1h, lookback=3)

          if (close_curr_1h > hma20_1h.iloc[-1]) and (mfi_curr_1h > 30) and (plus_di_curr_1h > 20) and (cmf_curr_1h > -0.20) and sart_1h_super_prep:
            if simdi_epoch - tum_hafiza[kural_tipi].get(clean_ticker, 0) > COOLDOWN_SECONDS:
              tetiklenen_str.append(f"• 🟠 {label} (MFi:{mfi_curr_1h:.1f}|CMF:{cmf_curr_1h:.2f})")
              toplam_puan += 30.0
              tum_hafiza[kural_tipi][clean_ticker] = simdi_epoch

        if tetiklenen_str:
          if toplam_puan == 0:
            toplam_puan = 30.0

          toplanan_sinyaller.append({
              "temiz_isim": temiz_isim,
              "fiyat": guncel_fiyat,
              "puan": toplam_puan,
              "stratejiler": tetiklenen_str
          })
          hafiza_kaydet(tum_hafiza)

      except Exception as e:
        print(f"Hata oluştu ({clean_ticker}): {e}")
        continue

  # --- KATEGORİZASYON VE TOPLU MESAJ GÖNDERİMİ ---
  if toplanan_sinyaller:
    toplanan_sinyaller.sort(key=lambda x: x["puan"], reverse=True)

    grup_3_fuze = []
    grup_2_fuze = []
    grup_1_fuze = []

    for item in toplanan_sinyaller:
      p = item["puan"]
      if p >= 60.0:
        grup_3_fuze.append(item)
      elif p >= 40.0:
        grup_2_fuze.append(item)
      else:
        grup_1_fuze.append(item)

    zaman_str = datetime.now(TZ_TR).strftime('%H:%M')

    if grup_3_fuze:
      icerik_listesi = []
      for s in grup_3_fuze:
        str_metni = "\n".join(s["stratejiler"])
        kart = (
            f"🚀🚀🚀 TOP SİNYAL - 👑 {s['puan']:.1f} Puan\n"
            f"📌 Hisse: 🟦 {s['temiz_isim']} 🟦 | Fiyat: ₺{s['fiyat']:.2f}\n"
            f"{str_metni}\n"
            "----------------------------"
        )
        icerik_listesi.append(kart)

      mesaj_3 = f"BIST Zirve Sinyaller (3 Fuze) [{zaman_str}]\n----------------------------\n" + "\n".join(icerik_listesi)
      send_ntfy(mesaj_3, "BIST Zirve Sinyaller (3 Fuze)")
      time.sleep(1)

    if grup_2_fuze:
      chunk_size = 3
      chunks = [grup_2_fuze[i:i + chunk_size] for i in range(0, len(grup_2_fuze), chunk_size)]
      total_parts = len(chunks)
      
      for part_idx, chunk in enumerate(chunks, 1):
        icerik_listesi = []
        for s in chunk:
          str_metni = "\n".join(s["stratejiler"])
          kart = (
              f"🚀🚀 GUCLU SINYAL - {s['puan']:.1f} Puan\n"
              f"📌 Hisse: 🟦 {s['temiz_isim']} 🟦 | Fiyat: ₺{s['fiyat']:.2f}\n"
              f"{str_metni}\n"
              "----------------------------"
          )
          icerik_listesi.append(kart)

        mesaj_2 = f"BIST Guclu Sinyaller (2 Fuze) [{part_idx}/{total_parts}] [{zaman_str}]\n----------------------------\n" + "\n".join(icerik_listesi)
        send_ntfy(mesaj_2, f"BIST Guclu Sinyaller (2 Fuze) [{part_idx}/{total_parts}]")
        time.sleep(1)

    if grup_1_fuze:
      for s in grup_1_fuze:
        str_metni = "\n".join(s["stratejiler"])
        mesaj_1 = (
            f"BIST Standart Sinyal [{zaman_str}]\n"
            "----------------------------\n"
            f"🚀 STANDART SINYAL - {s['puan']:.1f} Puan\n"
            f"📌 Hisse: 🟦 {s['temiz_isim']} 🟦 | Fiyat: ₺{s['fiyat']:.2f}\n"
            f"{str_metni}\n"
            "----------------------------"
        )
        send_ntfy(mesaj_1, f"BIST Standart Sinyal - {s['temiz_isim']}")
        time.sleep(1)

  print("\nTüm Hisseler 40'ar gruplar halinde tarandı ve süreç tamamlandı.")


if __name__ == "__main__":
  run_scanner()
