#!/usr/bin/python

import sys
import argparse
import datetime

def date_arg(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d')
def date_print(s):
    return datetime.datetime.strftime(s, '%Y-%m-%d')

parser = argparse.ArgumentParser("business-plan")
parser.add_argument("--target_income", help="Monthly expenses", type=int, default=5000)
parser.add_argument("--growth_rate", help="Monthly growth rate, a factor greater than 1", type=float, default=1.10)
parser.add_argument("--cpm", help="Monthly CPM, ad revenue per 1000 views", type=float, default=4.0)
parser.add_argument("--initial_date", help="Initial reference date YYYY-MM-DD", type=date_arg, default="2024-01-01")
parser.add_argument("--initial_subs", help="Initial reference sub count", type=int, default=1000)
parser.add_argument("--current_date", help="Current date", type=date_arg, default=datetime.datetime.now())
parser.add_argument("--current_subs", help="Current sub count", type=int, default=2000)
parser.add_argument("--current_monthly_views", help="Current views per month", type=int, default=10000)
 
parser.add_argument("--videos_per_week", help="How many videos you publish weekly", type=float, default=1)
parser.add_argument("--day_job_income", help="Income from current day job", type=int, default=10000)
parser.add_argument("--day_job_for_months", help="If you intend to stay at the day job for this many months", type=int, default=12)
parser.add_argument("--day_job_until_subs", help="If you intend to stay at the day job until reaching this many subs", type=int, default=0)
parser.add_argument("--brand_deal1_threshold", help="Future brand deal sub threshold", type=int, default=50000)
parser.add_argument("--brand_deal1_income", help="Future brand deal income per month", type=int, default=1000)
parser.add_argument("--brand_deal2_threshold", help="Future brand deal sub threshold", type=int, default=100000)
parser.add_argument("--brand_deal2_income", help="Future brand deal income per month", type=int, default=4000)
parser.add_argument("--verbose", help="Print extra messages about computations", type=int, default=4)


args = parser.parse_args()

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

expenses = args.target_income
growth_rate = args.growth_rate
cost_per_milli = args.cpm/1000
initial_subs = args.initial_subs
current_months = diff_month(args.current_date, args.initial_date)
current_subs = args.current_subs
videos_per_month = 52/12. * args.videos_per_week
current_views_per_month = args.current_monthly_views
verbose = args.verbose

max_months = 12*10

sub_view_ratio = current_views_per_month*1.0/current_subs  # how many subscribers view each video
current_growth_rate = (current_subs*1.0/initial_subs) ** (1.0/current_months)

if(verbose > 3):
    print("Arguments: %s" % sys.argv[1:])

print("Grew from %d subs on %s to %d on %s (%d months)" % (initial_subs, date_print(args.initial_date), \
    current_subs, date_print(args.current_date), current_months))

print("Target growth rate %.3f (achieved %.3f historically)" % (growth_rate, current_growth_rate))

print("Current views per month %d, per video %d, CPM $%.2f/1000" % (current_views_per_month, \
    current_views_per_month / videos_per_month, args.cpm))

other_job_income = args.day_job_income
other_job_months = args.day_job_for_months
other_job_threshold = args.day_job_until_subs

subs = [current_subs*growth_rate**(x) for x in range(0,max_months+1)]
new_subs_per_month = [x*(growth_rate-1.0) for x in subs]
view_counts_per_month = [sub_view_ratio * x for x in subs]
view_counts = [x / videos_per_month for x in view_counts_per_month]

#print("Future subscriber attach rate: %.5f" \
#    % (new_subs_per_month[0]/view_counts_per_month[0]))

adrev = [cost_per_milli * x for x in view_counts_per_month]
brand = [args.brand_deal2_income if subs[x] >= args.brand_deal2_threshold \
    else args.brand_deal1_income if subs[x] >= args.brand_deal1_threshold \
    else 0 for x in range(0,max_months+1)]
if other_job_months > 0:
    if(verbose > 3):
        print("Day job for the next %d months gives income %d" % (other_job_months, other_job_income))
    other_job = [other_job_income if x < other_job_months else 0 \
        for x in range(0,max_months+1)]
else:
    other_job = [other_job_income if subs[x] < other_job_threshold else 0 \
        for x in range(0,max_months+1)]
    other_job_months = sum(other_job) / other_job_income
    if(verbose > 3):
        print("Day job at income %d until %d subs means for %d months" % (other_job_income, other_job_threshhold, other_job_months))

revenue = [x+y for (x,y) in zip(adrev, brand)]
revenue2 = [x+y for (x,y) in zip(revenue, other_job)]

months_needed = len(filter(lambda x: x < expenses, revenue)) + 1
burn_needed = expenses*months_needed - sum(revenue2[:months_needed])

def round2(x):
    return round(x*100)/100
def p_monthly(a):
    return str(map(round2, a[:months_needed]))
def p_yearly(a):
    return str(map(round2, [a[i] for i in range(0, months_needed, 12)]))

if(verbose > 1):
    print("Per-video views: " + p_monthly(view_counts))

    print("Monthly subs: " + p_monthly(subs))
    print("Monthly new subs: " + p_monthly(new_subs_per_month))
    print("Monthly views: " + p_monthly(view_counts_per_month))
    print("Monthly ad revenue: " + p_monthly(adrev))
    print("Monthly brand revenue: " + p_monthly(brand))
    print("Monthly other revenue: " + p_monthly(other_job))
    print("Monthly total revenue: " + p_monthly(revenue2))
    print("Monthly percentage of income: " + p_monthly([x / expenses for x in revenue2]))

if(verbose > 0):
    print("Yearly subs: " + p_yearly(subs))
    print("Yearly ad revenue: " + p_yearly(adrev))
    print("Yearly brand revenue: " + p_yearly(brand))
    print("Yearly other revenue: " + p_yearly(other_job))
    print("Yearly total revenue: " + p_yearly(revenue2))

print("Monthly expenditure: " + str(expenses))
print("Burn needed: " + str(burn_needed))

print("Time at other job: %d months, %.3f years" \
    % (other_job_months, other_job_months/12.))
print("Time needed for profitability: %d months, %.3f years" \
    % (months_needed, months_needed/12.))
