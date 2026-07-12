/**
 * 表单验证规则
 * @description 统一的表单验证规则和错误消息
 */

/**
 * 验证规则配置
 */
export const validationRules = {
  // 用户名
  username: {
    pattern: /^[a-zA-Z0-9_]{3,20}$/,
    message: "用户名必须是3-20位字母、数字或下划线",
  },

  // 邮箱
  email: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    message: "请输入有效的邮箱地址",
  },

  // 手机号（中国大陆）
  phone: {
    pattern: /^1[3-9]\d{9}$/,
    message: "请输入有效的手机号码",
  },

  // 密码
  password: {
    minLength: 6,
    maxLength: 32,
    pattern: /^(?=.*[a-zA-Z])(?=.*\d).+$/,
    message: "密码至少6位，必须包含字母和数字",
  },

  // 强密码
  strongPassword: {
    minLength: 8,
    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
    message: "密码至少8位，必须包含大小写字母、数字和特殊字符",
  },

  // 金额
  amount: {
    pattern: /^(0|[1-9]\d*)(\.\d{1,2})?$/,
    message: "请输入有效的金额",
  },

  // 数量
  quantity: {
    pattern: /^[1-9]\d*$/,
    message: "请输入有效的数量（正整数）",
  },

  // 百分比
  percentage: {
    pattern: /^(100|[1-9]?\d)(\.\d{1,2})?%?$/,
    message: "请输入0-100之间的百分比",
  },

  // URL
  url: {
    pattern: /^https?:\/\/.+/,
    message: "请输入有效的URL（以http://或https://开头）",
  },

  // 日期
  date: {
    pattern: /^\d{4}-\d{2}-\d{2}$/,
    message: "请输入有效的日期（YYYY-MM-DD）",
  },

  // 邮政编码
  postalCode: {
    pattern: /^\d{6}$/,
    message: "请输入6位邮政编码",
  },

  // 身份证号
  idCard: {
    pattern: /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/,
    message: "请输入有效的身份证号码",
  },

  // 统一社会信用代码
  creditCode: {
    pattern: /^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$/,
    message: "请输入有效的18位统一社会信用代码",
  },

  // 银行账号
  bankAccount: {
    pattern: /^\d{10,25}$/,
    message: "请输入10-25位银行账号",
  },
} as const;

/**
 * 验证函数类型
 */
export type Validator = (value: any, formData?: Record<string, any>) => string | null;

/**
 * 必填验证
 */
export const required = (message = "此项为必填"): Validator => {
  return (value: any) => {
    if (value === null || value === undefined || value === "") {
      return message;
    }
    if (Array.isArray(value) && value.length === 0) {
      return message;
    }
    return null;
  };
};

/**
 * 最小长度验证
 */
export const minLength = (min: number, message?: string): Validator => {
  return (value: any) => {
    if (value && value.length < min) {
      return message || `最少需要${min}个字符`;
    }
    return null;
  };
};

/**
 * 最大长度验证
 */
export const maxLength = (max: number, message?: string): Validator => {
  return (value: any) => {
    if (value && value.length > max) {
      return message || `最多允许${max}个字符`;
    }
    return null;
  };
};

/**
 * 正则表达式验证
 */
export const pattern = (regex: RegExp, message = "格式不正确"): Validator => {
  return (value: any) => {
    if (value && !regex.test(value)) {
      return message;
    }
    return null;
  };
};

/**
 * 最小值验证
 */
export const min = (minValue: number, message?: string): Validator => {
  return (value: any) => {
    const num = Number(value);
    if (value !== "" && !isNaN(num) && num < minValue) {
      return message || `不能小于${minValue}`;
    }
    return null;
  };
};

/**
 * 最大值验证
 */
export const max = (maxValue: number, message?: string): Validator => {
  return (value: any) => {
    const num = Number(value);
    if (value !== "" && !isNaN(num) && num > maxValue) {
      return message || `不能大于${maxValue}`;
    }
    return null;
  };
};

/**
 * 邮箱验证
 */
export const email: Validator = pattern(
  validationRules.email.pattern,
  validationRules.email.message
);

/**
 * 手机号验证
 */
export const phone: Validator = pattern(
  validationRules.phone.pattern,
  validationRules.phone.message
);

/**
 * 密码验证
 */
export const password = (strength: "normal" | "strong" = "normal"): Validator => {
  const rule = strength === "strong"
    ? validationRules.strongPassword
    : validationRules.password;
  return (value: any) => {
    if (!value) return "密码不能为空";
    if (value.length < rule.minLength) {
      return `密码至少需要${rule.minLength}位`;
    }
    if (rule.pattern && !rule.pattern.test(value)) {
      return rule.message;
    }
    return null;
  };
};

/**
 * 确认密码验证
 */
export const confirmPassword = (passwordField: string): Validator => {
  return (value: any, formData?: Record<string, any>) => {
    if (formData && value !== formData[passwordField]) {
      return "两次输入的密码不一致";
    }
    return null;
  };
};

/**
 * URL验证
 */
export const url: Validator = pattern(
  validationRules.url.pattern,
  validationRules.url.message
);

/**
 * 整数验证
 */
export const integer = (message = "请输入整数"): Validator => {
  return (value: any) => {
    if (value && !/^\d+$/.test(value)) {
      return message;
    }
    return null;
  };
};

/**
 * 数字验证
 */
export const number = (message = "请输入数字"): Validator => {
  return (value: any) => {
    if (value && isNaN(Number(value))) {
      return message;
    }
    return null;
  };
};

/**
 * 金额验证
 */
export const amount = (message?: string): Validator => {
  return (value: any) => {
    if (value && !validationRules.amount.pattern.test(value)) {
      return message || validationRules.amount.message;
    }
    return null;
  };
};

/**
 * 自定义验证
 */
export const custom = (
  validator: (value: any) => boolean | string,
  message = "验证失败"
): Validator => {
  return (value: any) => {
    const result = validator(value);
    if (result === true) return null;
    if (typeof result === "string") return result;
    return message;
  };
};

/**
 * 组合验证器
 */
export const compose = (...validators: Validator[]): Validator => {
  return (value: any, formData?: Record<string, any>) => {
    for (const validator of validators) {
      const error = validator(value, formData);
      if (error) return error;
    }
    return null;
  };
};

/**
 * 表单字段验证配置
 */
export interface FieldValidation {
  validators?: Validator[];
  required?: boolean;
  message?: string;
}

/**
 * 表单验证配置
 */
export interface FormValidation {
  [fieldName: string]: FieldValidation;
}

/**
 * 验证表单
 */
export const validateForm = (
  formData: Record<string, any>,
  validationConfig: FormValidation
): { valid: boolean; errors: Record<string, string> } => {
  const errors: Record<string, string> = {};

  for (const [fieldName, config] of Object.entries(validationConfig)) {
    const value = formData[fieldName];

    // 检查必填
    if (config.required) {
      const requiredError = required(config.message)(value);
      if (requiredError) {
        errors[fieldName] = requiredError;
        continue;
      }
    }

    // 执行验证器
    if (config.validators && value !== "" && value !== null && value !== undefined) {
      for (const validator of config.validators) {
        const error = validator(value, formData);
        if (error) {
          errors[fieldName] = error;
          break;
        }
      }
    }
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors,
  };
};
