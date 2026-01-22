import { register_payment_method } from "@point_of_sale/app/store/pos_store";
import { BcaecrPay } from "@weha_smar_pos_bca_ecr/app/payment_deposit";

register_payment_method("bcaecr", BcaecrPay);




