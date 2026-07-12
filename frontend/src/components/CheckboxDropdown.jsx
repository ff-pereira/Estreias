import {useDropdown} from "../hooks/UseDropdown.jsx";


/**
 * @author ffpereira
 */
export default function CheckboxDropdown({ label, options, selected, setSelected, hideMargins=false }) {
  const { open, setOpen, dropdownRef } = useDropdown();

  return (
    <div ref={dropdownRef} className={`${hideMargins ? "mt-4" : "-mt-2 md:mt-4"} relative group`}> {/*onMouseEnter = {() => setOpen(true)} onMouseLeave={() => setOpen(false)*/}
      <div className="w-full px-3 py-[9px] md:py-2 border border-primary/25 rounded-md bg-gray-100 hover:bg-gray-200 cursor-pointer select-none"
        onClick={() => setOpen(prev => !prev)}
      >
        {selected.length === 0 ? label : `${label} (${selected.length})`}
      </div>

      {open && (
          <div className="absolute z-10 w-full bg-gray-100 border rounded shadow overflow-auto max-h-[30vh] overflow-y-auto scrollbar-minimal select-none">
            {options.length > 0 ?
              options.map(item => (
                <label
                  key={item.id}
                  className="flex items-center gap-2 px-3 py-2 text-sm cursor-pointer hover:bg-gray-200"
                >
                  <input
                    type="checkbox" className="accent-primary"
                    checked={selected.includes(String(item.id))}
                    onChange={e => {
                      setSelected(prev =>
                        e.target.checked
                          ? [...prev, String(item.id)]
                          : prev.filter(id => id !== String(item.id))
                      );
                    }}
                  />
                  {item.name}  {item.film_count != null && ` (${item.film_count})`} {item.count != null && ` (${item.count})`}
                </label>
              )
            ):
                <div className="px-3 py-2 text-sm text-gray-400 italic">No options available</div>
            }
          </div>
      )}
    </div>
  );
}