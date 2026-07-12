/**
 * @author ffpereira
 */
export default function More({ pagination, direction, loadPage, rotation=0 }){
    let thereAreMore = false;

    if(pagination){
        const { offset, count, total } = pagination;

          if (direction === "next") {
            thereAreMore = offset + count < total;
          }
          if (direction === "prev") {
            thereAreMore = offset > 0;
          }
    }

    return (
        <div className="flex justify-center items-center">
            {thereAreMore &&
                <button className="cursor-pointer p-2 bg-tealish/50 rounded-full text-dark-primary transform hover:scale-110 transition ease-in-out duration-200" onClick={loadPage}>
                    <svg fill="none" viewBox="0 0 24 24" strokeWidth="2.5" stroke="currentColor" className="w-6 h-6" style={{ transform: `rotate(${rotation}deg)` }}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
                    </svg>
                </button>
            }
        </div>
    );
}