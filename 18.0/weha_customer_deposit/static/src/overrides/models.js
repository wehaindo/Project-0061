import { register_payment_method } from "@point_of_sale/app/store/pos_store";
import { DepositPay } from "@weha_customer_deposit/app/payment_deposit";

register_payment_method("deposit", DepositPay);




