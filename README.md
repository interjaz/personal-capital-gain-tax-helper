### Disclaimer
* You should seek independent professional financial advice  
* This is intended for personal use
* There is no guarantee that results are correct
* There is no warranty on this software
* Use at own risk

### How to use it
1. Create api_key.py file and populate it with
   ```python
   ALPHA_VANTAGE_KEY = "MY_API_KEY"
   ```
   You can get MY_API_KEY after registering with https://www.alphavantage.co/
   
1. Update transactions.tsv with values you want

1. Install all required python libraries

   ```python
   pip3 install requests
   ```
1. Run script

   ```python
   python3 main.py
   ```

### How calculation is being made

#### Rules

Calculation algorithm is using following rules
* Base monetary unit is pound not pence [1]
* Income is rounded DOWN [1]
* Tax is rounded UP [1]
* UK tax year starts at 6th of April and ends on 5th of April [2]
* Bed and ISA transactions cannot be identified as "same day" or "bed and breakfast" transactions [3] [4] 
* "Bed and breakfast" or "same day" rules apply to all other transactions [5]
* Assets (shares/coins) are calculated assuming they fall into Section 104 holding [6]
* No stamp duty or any other costs are taken into calculation

#### Reference
* [1] https://www.gov.uk/hmrc-internal-manuals/self-assessment-manual/sam121370
* [2] https://www.gov.uk/self-assessment-tax-returns/deadlines
* [3] https://www.barclays.co.uk/smart-investor/investments/moving-investments/more-about-bed-and-isa/
* [4] https://forums.moneysavingexpert.com/discussion/5850109/bed-isa-vs-bed-breakfast/p2
* [5] https://www.gov.uk/hmrc-internal-manuals/capital-gains-manual/cg51560
* [6] https://www.gov.uk/hmrc-internal-manuals/capital-gains-manual/cg51555

### Example

1. John bought 1000 shares of company X plc each valued at £1.00 on 20th May 2019
1. John bought 500 shares of company Y plc each valued at £2.00 each on 21st of May 2019
1. John bought 200 shares of company X plc valued at £1.50 on 30th of May 2019
1. John sold 10 shares of company X plc valued at £1.90 on 1st of August 2019
1. John bought 100 shares of company X plc valued at £2.00 on 1st of August 2019
1. John sold 50 shares of company X plc valued at £2.50 on 10th of August 2019
1. John sold 300 shares of company X plc valued at £1.75 on 10th of December 2019
1. John bought 100 shares of company X plc valued at £2.20 on 1st of February 2020

There are two assets, X and Y, each form separate Section 104 holding and needs to be calculated separately.
As Y plc is trivial, we will skip it and provide details only for X plc company.

**2019-05-20**  
1000 shares were bought, £1.00 each.  
Section 104 holding at cost of £1000, with 1000 shares.

**2019-05-30**  
500 shares were bought, £1.50 each.  
Section 104 holding at cost of £1750 (1000 + 750), with 1500 shares.

**2019-08-01 - 2019-08-10**  
100 shares were bought, £2.00 each.  
10 shares were sold, £1.90 each.  
50 shares were sold, £2.50 each.  

(Same day rule)  
100 and 10 shares are matched by same day rule   
No capital loss or gain   
Remaining shares 90

(30 days rule)  
90 shares and 50 shares are matched by 30 days rule  
No capital loss or gain  
Remaining shares 40

(Section 104 holding)  
Section 104 holding cost of £1830 (1000 + 750 + 80), with 1540 shares.

**2019-12-10**  
300 shares were sold, £1.75 each.  
Capital gain = (300 * £1.75) - (300 / 1540 * £1830) = 168.50  
Section 104 holding cost of £1473.50 (1240/1540 * 1830), with 1240 shares

**2019-02-01**  
100 shares bought sold, £2.20 each.  
Section 104 holding cost of £1693.50 (1473.50 + 100 * 2.20), with 1340 shares

**Taxable capital gain**  
Capital gain = £168.50  
Capital loss = None  
Total capital gain during tax year £168.50  
Capital tax allowance £12300, 20% after that   

In this case all gain can be covered by allowance.