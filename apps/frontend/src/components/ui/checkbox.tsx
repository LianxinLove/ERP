/**
 * Checkbox component
 * @description Checkboxes allow users to select multiple items from a list
 */

"use client";

import * as React from "react";
import { Check } from "lucide-react";

export interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'checked'> {
  checked?: boolean | "indeterminate";
  onCheckedChange?: (checked: boolean | "indeterminate") => void;
}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, checked, onCheckedChange, ...props }, ref) => {
    const [internalChecked, setInternalChecked] = React.useState<boolean>(
      checked === true
    );

    React.useEffect(() => {
      setInternalChecked(checked === true);
    }, [checked]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setInternalChecked(e.target.checked);
      onCheckedChange?.(e.target.checked);
    };

    return (
      <div className="relative inline-flex items-center">
        <input
          type="checkbox"
          ref={ref}
          checked={internalChecked}
          onChange={handleChange}
          className="peer appearance-none h-4 w-4 border border-primary rounded-sm cursor-pointer transition-all checked:bg-primary checked:border-primary"
          {...props}
        />
        <Check
          className={`absolute pointer-events-none h-3 w-3 text-white transition-opacity ${
            internalChecked ? "opacity-100" : "opacity-0"
          }`}
        />
      </div>
    );
  }
);

Checkbox.displayName = "Checkbox";

export { Checkbox };
