import {useDropdown} from "../hooks/UseDropdown.jsx";


/**
 * @author ffpereira
 */
export default function SortDropdown({ label, options, selected, setSelected }) {
  const selectedOption = options.find(o => o.id === selected);
  const { open, setOpen, dropdownRef } = useDropdown();

  return (
    <div ref={dropdownRef} className="relative group w-full">
      <div
        className="text-sm md:text-base text-center md:text-left px-2 md:px-3 py-1.5 md:py-2 cursor-pointer rounded-md bg-primary/30 hover:bg-primary/40 text-dark-primary duration-200 select-none"
        onClick={() => setOpen(prev => !prev)}
      >
        {selectedOption ? (
            <>
              <span className="hidden md:inline font-semibold">{label}:&nbsp;</span>{" "}
              <span className="hidden md:inline tracking-tight">{selectedOption.name}</span>
              <span className="md:hidden font-semibold">{label}</span>
              <span className="-mt-1 text-xs md:hidden block tracking-tight">{selectedOption.name}</span>
            </>
        ) : (
            <span className="font-semibold">{label}</span>
        )}
      </div>

      {open && (
          <div
              className="absolute z-10 mt-1 w-full bg-white border border-primary/30 rounded shadow max-h-[30vh] overflow-y-auto">
          {options.length > 0 ? (
            options.map(item => (
              <div
                key={item.id} onClick={() => {setSelected(item.id); setOpen(false);}}
                className={`px-2 md:px-3 py-2 text-xs md:text-sm text-center md:text-left cursor-pointer hover:bg-primary/10 text-darker-primary
                ${selected === item.id ? "bg-primary/15 font-semibold" : ""}`}
              >
                {item.name === "Cinematographer" ? "Camera" : item.name}
              </div>
            ))
          ) : (
            <div className="px-3 py-2 text-sm text-darker-primary italic">No options available</div>
          )}
        </div>
      )}
    </div>
  );
}
