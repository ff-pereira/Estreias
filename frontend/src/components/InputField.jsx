/**
 * @author ffpereira
 */
export default function InputField({ name, label, type, placeholder, error, fieldRef, value, onChange }) {
    return (
        <div id={name} className="my-4 mb-2 md:mb-4">
            {label && <label className="block text-sm mb-1">{label}</label>}
            <input
                id={name}
                type={type || 'text'}
                placeholder={placeholder}
                ref={fieldRef}
                value={value}
                onChange={onChange}
                className="input-field "
            />
            {error && <p className="text-sm text-red-500 mt-1">{error}</p>}
        </div>
    );
}