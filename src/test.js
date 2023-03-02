

const avg_monthly = 0;
const safety_months = 3;
const bank_total = 0;
budgeted_months();


function budgeted_months(avg_monthly, safety_months, bank_total){
    // Takes in current savings, and month expenditures.
    //Calculates livable months without income.

    const safety_net = avg_monthly * safety_months;
    const runway = bank_total - safety_net;
    const result = Math.floor(runway/avg_monthly);
    return result;
}