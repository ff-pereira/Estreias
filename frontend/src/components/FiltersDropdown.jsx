import {useDropdown} from "../hooks/UseDropdown.jsx";


/**
 * @author ffpereira
 */
export default function FiltersDropdown({ children, clearFilters }) {
  const { open, setOpen, dropdownRef } = useDropdown();

  return (
    <div ref={dropdownRef}>
      <button
        onClick={() => setOpen(prev => !prev)}
        className="p-2 rounded-full cursor-pointer bg-primary/30 hover:bg-primary/40 flex items-center text-dark-primary hover:scale-110 transition ease-in-out duration-200"
      >
        <span className={`transition-transform duration-200`}>
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round"
                    d="M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 0 1-.659 1.591l-5.432 5.432a2.25 2.25 0 0 0-.659 1.591v2.927a2.25 2.25 0 0 1-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 0 0-.659-1.591L3.659 7.409A2.25 2.25 0 0 1 3 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0 1 12 3Z"/>
            </svg>

        </span>
      </button>

      {open && (
          <div className="absolute right-0 flex flex-col md:flex-row items-stretch md:items-center justify-center z-50 mt-2 w-full bg-primary/90 rounded-md shadow-lg px-4 pb-4">
            <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-x-4">{children}</div>
            <button onClick={clearFilters} className="flex md:ml-4 mt-4 col-span-full bg-accent text-white select-none
            hover-text-colorless cursor-pointer rounded-md p-2 text-center items-center justify-center gap-2">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12"/>
              </svg>
              <span>Clear Filters</span>
            </button>
          </div>

      )}
    </div>
  );
}