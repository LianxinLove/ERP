/**
 * 通用表单Schema
 * @description 使用 Zod 定义的表单验证规则
 */

import { z } from "zod";

/**
 * 用户相关Schema
 */
export const userFormSchema = z.object({
  username: z
    .string()
    .min(3, "用户名至少3个字符")
    .max(20, "用户名最多20个字符")
    .regex(/^[a-zA-Z0-9_]+$/, "用户名只能包含字母、数字和下划线"),
  email: z.string().email("请输入有效的邮箱地址"),
  full_name: z.string().optional(),
  phone: z
    .string()
    .regex(/^1[3-9]\d{9}$/, "请输入有效的手机号码")
    .optional()
    .or(z.literal("")),
  password: z
    .string()
    .min(6, "密码至少6个字符")
    .regex(/^(?=.*[a-zA-Z])(?=.*\d)/, "密码必须包含字母和数字")
    .optional(),
});

export type UserFormData = z.infer<typeof userFormSchema>;

/**
 * 密码修改Schema
 */
export const passwordChangeSchema = z
  .object({
    current_password: z.string().min(1, "请输入当前密码"),
    new_password: z
      .string()
      .min(6, "新密码至少6个字符")
      .regex(/^(?=.*[a-zA-Z])(?=.*\d)/, "密码必须包含字母和数字"),
    confirm_password: z.string().min(1, "请确认新密码"),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "两次输入的密码不一致",
    path: ["confirm_password"],
  });

export type PasswordChangeFormData = z.infer<typeof passwordChangeSchema>;

/**
 * 部门Schema
 */
export const departmentFormSchema = z.object({
  name: z.string().min(1, "部门名称不能为空").max(100, "部门名称最多100个字符"),
  code: z
    .string()
    .min(1, "部门编码不能为空")
    .max(50, "部门编码最多50个字符")
    .regex(/^[A-Z0-9_]+$/, "部门编码只能包含大写字母、数字和下划线"),
  parent_id: z.number().optional(),
  leader_id: z.number().optional(),
  description: z.string().max(500, "描述最多500个字符").optional(),
  sort_order: z.number().int().min(0).default(0),
});

export type DepartmentFormData = z.infer<typeof departmentFormSchema>;

/**
 * 员工Schema
 */
export const employeeFormSchema = z.object({
  user_id: z.number().optional(),
  employee_no: z
    .string()
    .min(1, "员工编号不能为空")
    .max(50, "员工编号最多50个字符"),
  department_id: z.number().optional(),
  position_id: z.number().optional(),
  entry_date: z.string().optional(),
  status: z.enum(["active", "resigned"]).default("active"),
});

export type EmployeeFormData = z.infer<typeof employeeFormSchema>;

/**
 * 供应商Schema
 */
export const supplierFormSchema = z.object({
  name: z.string().min(1, "供应商名称不能为空").max(200, "供应商名称最多200个字符"),
  code: z
    .string()
    .min(1, "供应商编码不能为空")
    .max(50, "供应商编码最多50个字符"),
  contact_person: z.string().max(100, "联系人最多100个字符").optional(),
  contact_phone: z
    .string()
    .regex(/^1[3-9]\d{9}$/, "请输入有效的手机号码")
    .optional()
    .or(z.literal("")),
  email: z.string().email("请输入有效的邮箱地址").optional().or(z.literal("")),
  address: z.string().max(500, "地址最多500个字符").optional(),
  tax_no: z.string().max(50, "税号最多50个字符").optional(),
  bank_name: z.string().max(100, "开户行最多100个字符").optional(),
  bank_account: z
    .string()
    .regex(/^\d{10,25}$/, "请输入10-25位银行账号")
    .optional()
    .or(z.literal("")),
  credit_level: z.enum(["A", "B", "C", "D"]).optional(),
  status: z.enum(["active", "inactive"]).default("active"),
});

export type SupplierFormData = z.infer<typeof supplierFormSchema>;

/**
 * 客户Schema
 */
export const customerFormSchema = z.object({
  name: z.string().min(1, "客户名称不能为空").max(200, "客户名称最多200个字符"),
  code: z
    .string()
    .min(1, "客户编码不能为空")
    .max(50, "客户编码最多50个字符"),
  contact_person: z.string().max(100, "联系人最多100个字符").optional(),
  contact_phone: z
    .string()
    .regex(/^1[3-9]\d{9}$/, "请输入有效的手机号码")
    .optional()
    .or(z.literal("")),
  email: z.string().email("请输入有效的邮箱地址").optional().or(z.literal("")),
  address: z.string().max(500, "地址最多500个字符").optional(),
  credit_limit: z.number().min(0, "信用额度不能为负数").optional(),
  credit_level: z.enum(["A", "B", "C", "D"]).optional(),
  status: z.enum(["active", "inactive"]).default("active"),
});

export type CustomerFormData = z.infer<typeof customerFormSchema>;

/**
 * 产品Schema
 */
export const productFormSchema = z.object({
  name: z.string().min(1, "产品名称不能为空").max(200, "产品名称最多200个字符"),
  code: z
    .string()
    .min(1, "产品编码不能为空")
    .max(50, "产品编码最多50个字符"),
  category_id: z.number().optional(),
  specification: z.string().max(200, "规格型号最多200个字符").optional(),
  unit: z.string().max(20, "单位最多20个字符").optional(),
  purchase_price: z.number().min(0, "采购价不能为负数").optional(),
  sale_price: z.number().min(0, "销售价不能为负数").optional(),
  safe_stock: z.number().int().min(0, "安全库存不能为负数").default(0),
  status: z.enum(["active", "inactive"]).default("active"),
  description: z.string().max(1000, "描述最多1000个字符").optional(),
});

export type ProductFormData = z.infer<typeof productFormSchema>;

/**
 * 仓库Schema
 */
export const warehouseFormSchema = z.object({
  name: z.string().min(1, "仓库名称不能为空").max(100, "仓库名称最多100个字符"),
  code: z
    .string()
    .min(1, "仓库编码不能为空")
    .max(50, "仓库编码最多50个字符"),
  address: z.string().max(500, "地址最多500个字符").optional(),
  manager_id: z.number().optional(),
  status: z.enum(["active", "inactive"]).default("active"),
  description: z.string().max(500, "描述最多500个字符").optional(),
});

export type WarehouseFormData = z.infer<typeof warehouseFormSchema>;

/**
 * 采购订单Schema
 */
export const purchaseOrderFormSchema = z.object({
  supplier_id: z.number().min(1, "请选择供应商"),
  expected_date: z.string().optional(),
  discount_rate: z.number().min(0).max(100).default(0),
  tax_rate: z.number().min(0).max(100).default(0),
  total_amount: z.number().min(0, "总金额不能为负数").default(0),
  remark: z.string().max(500, "备注最多500个字符").optional(),
});

export type PurchaseOrderFormData = z.infer<typeof purchaseOrderFormSchema>;

/**
 * 销售订单Schema
 */
export const salesOrderFormSchema = z.object({
  customer_id: z.number().min(1, "请选择客户"),
  expected_date: z.string().optional(),
  discount_rate: z.number().min(0).max(100).default(0),
  tax_rate: z.number().min(0).max(100).default(0),
  total_amount: z.number().min(0, "总金额不能为负数").default(0),
  remark: z.string().max(500, "备注最多500个字符").optional(),
});

export type SalesOrderFormData = z.infer<typeof salesOrderFormSchema>;

/**
 * 会计科目Schema
 */
export const accountFormSchema = z.object({
  name: z.string().min(1, "科目名称不能为空").max(100, "科目名称最多100个字符"),
  code: z
    .string()
    .min(1, "科目编码不能为空")
    .max(20, "科目编码最多20个字符")
    .regex(/^\d+(\.\d+)?$/, "科目编码格式不正确"),
  parent_id: z.number().optional(),
  type: z.enum(["asset", "liability", "equity", "revenue", "expense"]),
  direction: z.enum(["debit", "credit"]).default("debit"),
  description: z.string().max(500, "描述最多500个字符").optional(),
});

export type AccountFormData = z.infer<typeof accountFormSchema>;

/**
 * 搜索表单Schema
 */
export const searchFormSchema = z.object({
  keyword: z.string().optional(),
  status: z.string().optional(),
  date_from: z.string().optional(),
  date_to: z.string().optional(),
  page: z.number().int().min(1).default(1),
  page_size: z.number().int().min(1).max(100).default(20),
});

export type SearchFormData = z.infer<typeof searchFormSchema>;

/**
 * 登录Schema
 */
export const loginFormSchema = z.object({
  username: z.string().min(1, "请输入用户名"),
  password: z.string().min(1, "请输入密码"),
  remember: z.boolean().optional(),
});

export type LoginFormData = z.infer<typeof loginFormSchema>;

/**
 * 获取所有Schema的类型
 */
export type FormSchemaType = {
  user: UserFormData;
  passwordChange: PasswordChangeFormData;
  department: DepartmentFormData;
  employee: EmployeeFormData;
  supplier: SupplierFormData;
  customer: CustomerFormData;
  product: ProductFormData;
  warehouse: WarehouseFormData;
  purchaseOrder: PurchaseOrderFormData;
  salesOrder: SalesOrderFormData;
  account: AccountFormData;
  search: SearchFormData;
  login: LoginFormData;
};
