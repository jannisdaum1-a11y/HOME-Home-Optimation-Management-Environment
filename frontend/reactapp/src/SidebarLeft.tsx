import './SidebarLeft.css'

import assets from './assets/assets.json'

const excludeAssets: string[] = ['Config', "EV"];

type AssetData = {
    image?: string | null;
    [key: string]: unknown;
};
type AssetIconProps = {
    name: string,
    data: AssetData
}

function AssetIcon({name, data}: AssetIconProps){
    const image_path = data.image;

    const handleTouchStart = (event: React.TouchEvent<HTMLDivElement>) => {
        event.preventDefault();
        (window as Window & {__pendingAsset?: string}).__pendingAsset = name;
    };

    return (
        <div className='AssetIcon' key={name}
            draggable
            onDragStart={(e) => e.dataTransfer.setData("asset", name)}
            onTouchStart={handleTouchStart}>
            <img src={image_path ?? ""} alt={name} draggable={false}/>
            <p>{name}</p>
        </div>
    )
}
function SidebarLeft() {
    return (
        <div className="SideBarLeft">
            {Object.entries(assets).map(([name, data]) => (
                !excludeAssets.includes(name) &&
                <AssetIcon name={name} data={data}></AssetIcon>
            ))}
        </div>
    );
}

export default SidebarLeft